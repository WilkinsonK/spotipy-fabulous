"""
Defines the different objects responsible for
requesting authentication tokens from the target
host.

Specifically these classes utilizes the methods
(or Authentication Flows) described by OAuth2.0
using RESTful callouts.
"""

# --------------------------------------------- #
# Authorization Flow Objects. Below is a series
# of derivatives of the `BaseAuthFlowClient`
# object. These classes represent the different
# strategies available for making authentication
# requests to a target host.
# --------------------------------------------- #

import http, urllib.parse as urlparse

import requests

from ampyr import errors, factories as ft, protocols as pt, typedefs as td
from ampyr import cache
from ampyr.oauth2 import base, configs, hosts, tokens


def _aquire_token(flow: base.SimpleOAuth2Flow, key: str, *,
    factory: ft.OptTokenMetaDataFT = None) -> td.TokenMetaData:
    """
    Retrieves an access token from the target
    authentication server. This function first
    checks for valid token data that was
    previously cached, then makes a callout if no
    valid data exists.
    """

    # Initial lookup for a token from the
    # `OAuth2Flow`'s cache manager.
    data = flow.cache_manager.find(key)

    # Validate the token data found.
    scope = tokens.normalize_scope(flow.auth_config.scope or "")
    state = tokens.validate(data, scope=scope)

    if state is tokens.TokenState.ISVALID and data:
        return data

    if state is tokens.TokenState.EXPIRED and data:
        payload = td.TokenMetaData({
            "refresh_token": data["refresh_token"],
            "grant_type": "refresh_token"})
    elif factory:
        payload = factory()

    # Token either required a refresh or was
    # invalid. Get new token data and try again.
    data = _request_token(flow, payload)
    if data and "scope" not in data:
        data["scope"] = scope
    flow.cache_manager.save(key, data) #type: ignore[arg-type]

    return _aquire_token(flow, key, factory=factory)


def _request_token(flow: base.SimpleOAuth2Flow, payload: td.TokenMetaData):
    """
    Sends and outbound call to the target
    authentication server requesting a token for
    access.
    """

    response = flow.session.post(
        flow.url_for_token,
        data=payload,
        headers=flow.requests_config.headers,
        timeout=flow.requests_config.timeouts)

    # Test if there was and issue from the
    # callout, handle any subsequent errors.
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        _handle_http_error(error)
    else:
        data = td.TokenMetaData(response.json()) #type: ignore[misc]
        tokens.set_expires(data)
        return data


def _handle_http_error(error: requests.HTTPError):
    """Handle some HTTP exception."""

    status = http.HTTPStatus(error.response.status_code)
    raise errors.OAuth2HttpError("something went wrong.", status=status)


def _make_search_key(config: configs.AuthConfig, default: td.OptString = None):
    """
    Render a cache search key using this
    credentials object.
    """

    name = config.client_userid or default or "credentials"
    return "{}[{}]".format(name, config.client_id)


def _make_param_url(baseurl: str, payload: td.MetaData):
    """
    Returns the given baseurl with the given
    parameters joined to it.
    """

    # Remove any null values.
    payload = _normalize_payload(payload)
    return "?".join([baseurl, urlparse.urlencode(payload)])


def _normalize_payload(payload: td.MetaData):
    """
    Filter out any fields in the payload that do
    not meet the condition. Condition is
    "exclude objects that are not truthy".

    NOTE: This function returns a **copy** of the
    given payload, not the original modified.
    """

    cleaned_data = payload.copy()
    condition    = (lambda o: o != None)

    for key, value in payload.items():
        if condition(value):
            continue
        cleaned_data.pop(key)

    return td.MetaData(cleaned_data)


class NullFlow(base.SimpleOAuth2Flow):
    """
    Effectively does nothing. This object acts as
    a placeholder in the event no `OAuth2Flow`
    object or type was provided. It's subsequent
    methods act without modifying it's inputs, or
    returning empty or null data.
    """

    def aquire(self):
        return td.NotAToken


class CredentialsFlow(base.SimpleOAuth2Flow):
    """
    This `CredentialsFlow` object is used
    in server-to-server authentication. Only
    endpoints that do not access user information
    are authorized using this strategy. This
    limits the usage of this client to only
    making callouts that require no scope(s).

    This `OAuth2Flow` requires no user
    interaction.
    """

    def aquire(self):
        key     = _make_search_key(self.auth_config, "client_credentials")
        factory = lambda: td.TokenMetaData({"grant_type": "client_credentials"})
        return _aquire_token(self, key, factory=factory)["access_token"]


class AuthorizationFlow(base.SimpleOAuth2Flow):
    """
    This `AuthorizationFlow` object is used in
    in app-based authentication primarily.
    Provided an access scope, this flow grants
    a wider range of access to the target host,
    limited by what the target user allows.

    This `AuthFlowClient` does require user
    interaction.
    """

    oauth_param_keys: tuple[str, ...] = (
        "client_id",
        "redirect_uri",
        "scope",
        "state",
        "show_dialogue",
        "response_type")
    """
    Sequence of names expected to be used in an
    oauth token request.
    """

    oauth_code: td.Optional[int]
    """
    Code representing the state of
    authentication.
    """

    show_dialogue: bool

    @property #type: ignore[override]
    def url_for_oauth(self):
        params = {
            k:v for k,v in self.auth_config.asdict().items()
            if k in self.oauth_param_keys}

        params["redirect_uri"]  = self.auth_config.url_for_redirect
        params["show_dialogue"] = self.show_dialogue
        params["response_type"] = "code"

        base = getattr(self, "_url_for_oauth")
        return _make_param_url(base, params)

    @url_for_oauth.setter
    def url_for_oauth(self, value):
        setattr(self, "_url_for_oauth", value)

    def aquire(self):
        key = _make_search_key(self.auth_config, "authorization_code")

        def factory():
            if not self.oauth_code:
                self.oauth_code = hosts.get_user_auth(self)
            return _normalize_payload({
                "redirect_uri": self.auth_config.url_for_redirect,
                "grant_type": "authorization_code",
                "code": self.oauth_code,
                "scope": self.auth_config.scope,
                "state": self.auth_config.state})

        return _aquire_token(self, key, factory=factory)["access_token"]

    def __init__(self, *args, show_dialogue: bool = False, **kwds):
        super().__init__(*args, **kwds)

        # Attributes used for browser behavior.
        self.show_dialogue = show_dialogue
        self.oauth_code    = None


class PKCEFlow(base.SimpleOAuth2Flow):
    """
    Proof Key for Code Exchange.

    This `PKCEFlow` object is used for `user` and
    `non-user` endpoints. When this auth flow
    requests access for the first time, a target
    user will be prompted for approval.

    This is the recommended strategy for
    mobile/desktop applications.
    """

    oauth_param_keys: tuple[str, ...] = (
        "client_id",
        "redirect_uri",
        "code_challenge",
        "scope",
        "state",
        "code_challenge_method",
        "response_type")
    """
    Sequence of names expected to be used in an
    oauth token request.
    """

    oauth_challenge_method: str = "S256" # SHA256
    """
    Method of encryption used for validating
    token requests.
    """

    oauth_code: td.Optional[int]
    """
    Code representing the state of
    authentication.
    """

    @property #type: ignore[override]
    def url_for_oauth(self):
        params = {
            k:v for k,v in self.auth_config.asdict().items()
            if k in self.oauth_param_keys}

        params["redirect_uri"]          = self.auth_config.url_for_redirect
        params["response_type"]         = "code"
        params["code_challenge_method"] = self.oauth_challenge_method

        base = getattr(self, "_url_for_oauth")
        return _make_param_url(base, params)

    @url_for_oauth.setter
    def url_for_oauth(self, value):
        setattr(self, "_url_for_oauth", value)

    def aquire(self):
        key = _make_search_key(self.auth_config, "pkce")

        def factory():
            if not self.oauth_code:
                self.oauth_code = hosts.get_user_auth(self)
            return _normalize_payload({
                "redirect_uri": self.auth_config.url_for_redirect,
                "grant_type": "authorization_code",
                "code": self.oauth_code,
                "client_id": self.auth_config.client_id,
                "code_verifier": self.auth_config.code_verifier})

        return _aquire_token(self, key, factory=factory)["access_token"]

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.requests_config.headers.update({
            "Content-Type": "application/x-www-form-urlencoded"})
        self.oauth_code = None
