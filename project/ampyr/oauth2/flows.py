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
from ampyr.oauth2 import configs, tokens

DEFAULT_OAUTH_URL = "http://127.0.0.1"
"""
Default base url for making making calls to some
`OAuth2.0` server.
"""

DEFAULT_TOKEN_URL = "/".join([DEFAULT_OAUTH_URL, "token"])
"""
Default base url for making token requests to
some `OAuth2.0` server.
"""


class SimpleOAuth2Flow(pt.OAuth2Flow):
    """
    Basic implementation. Defines constructor for
    all subsequent derivatives.

    Warning: Not meant to be used directly.
    """

    cache_manager: pt.CacheManager
    """
    Interacts with some cache that is expected to
    store token data.
    """

    cache_class: type[pt.CacheManager]
    """
    Class used to build new `CacheManager`
    objects.
    """

    cache_factory: ft.OptCacheFT
    """Constructs new `CacheManager` objects."""

    session: td.Session
    """
    A requests session. Used for making RESTful
    transactions.
    """

    session_factory: ft.OptSessionFT
    """
    Constructs new `requests.Session` objects.
    """

    url_for_oauth: str
    """
    Points to the URL used for `OAuth2.0`.
    """

    url_for_token: str
    """
    Points to the URL responsible for requesting
    auth tokens.
    """

    @property
    def auth_config(self):
        return self.__auth_config__

    @property
    def requests_config(self):
        return self.__requests_config__

    __auth_config__:     configs.AuthConfig
    __requests_config__: configs.RequestsConfig

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, tback):
        return

    def __init__(self, client_id: str, client_secret: str,
        client_username: td.OptString = None, *,
        cache_class: td.Optional[type[pt.CacheManager]] = None,
        cache_factory: ft.OptCacheFT = None,
        session_factory: ft.OptSessionFT = None,
        headers: td.OptRequestHeaders = None,
        scope: td.OptAuthScope = None,
        state: td.OptString = None,
        timeouts: td.Optional[tuple[float, ...]] = None,
        url_for_oauth: td.OptString = None,
        url_for_redirect: td.OptString = None,
        url_for_token: td.OptString = None):
        """Build some `OAuth2Flow` object."""

        # Initialize internal configs.
        self._new_auth_config(
            client_id,
            client_secret,
            client_username=client_username,
            url_for_redirect=url_for_redirect,
            scope=scope,
            state=state)
        self._new_requests_config(headers, timeouts)

        # Cache manager construction components.
        # TODO: define basic cache classes.
        self.cache_class   = cache_class or cache.MemoryCacheManager
        self.cache_factory = cache_factory

        # Session construction components.
        self.session_factory = session_factory

        # URL parsing and components.
        self.url_for_oauth = url_for_oauth or DEFAULT_OAUTH_URL
        self.url_for_token = url_for_token or DEFAULT_TOKEN_URL

        # Initialize internal access objects,
        # managers, handlers, etc.
        self._new_cache_manager()
        self._new_session()

    def _new_auth_config(self, *args, **kwds):
        """
        Generates a configuration object for
        OAuth values.
        """

        args = args + (tokens.make_verifier(),)

        inst = ft.generic_make(
            configs.AuthConfig,
            gt_args=args,
            gt_kwds=kwds)
        inst.code_challenge = tokens.make_challenge(inst)

        self.__auth_config__ = inst

    def _new_cache_manager(self, *args, **kwds) -> None:
        """
        Creates a `CacheManager` object using
        this flows internal factory. The new
        manager is then assigned to this flow.
        """

        inst = ft.generic_make(self.cache_class,
            gt_factory=self.cache_factory,
            gt_args=args,
            gt_kwds=kwds)

        self.cache_manager = inst

    def _new_requests_config(self, *args, **kwds):
        """
        Generates a configuration object for
        basic requests values.
        """

        headers, args = args[0], args[1:]

        if not headers:
            headers = tokens.make_headers(self.auth_config)
        args = (headers,) + args

        inst = ft.generic_make(
            configs.RequestsConfig,
            gt_args=args,
            gt_kwds=kwds)

        self.__requests_config__ = inst

    def _new_session(self, *args, **kwds) -> None:
        """
        Creates a `requests.Session` object using
        this flows internal factory. The new
        session is then assigned to this flow.
        """

        inst = ft.generic_make(td.Session,
            gt_factory=self.session_factory,
            gt_args=args,
            gt_kwds=kwds)

        self.session = inst


def _aquire_token(flow: SimpleOAuth2Flow, key: str, *,
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
    flow.cache_manager.save(key, data)
    return _aquire_token(flow, key, factory=factory)


def _request_token(flow: SimpleOAuth2Flow, payload: td.TokenMetaData):
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
    raise errors.OAuth2Exception("something went wrong.", status=status)


def _make_search_key(config: configs.AuthConfig, default: td.OptString = None):
    """
    Render a cache search key using this
    credentials object.
    """

    name = config.client_username or default or "credentials"
    return ":".join([name, config.client_id])


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


class ClientCredentials(SimpleOAuth2Flow):
    """
    This `ClientCredentialsFlow` object is used
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


class Authorization(SimpleOAuth2Flow):
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

    oauth_code: None | int
    """
    Code representing the state of
    authentication.
    """

    show_dialogue: bool

    @property
    def url_for_oauth(self):
        params = td.MetaData({
            k:v for k,v in self.auth_config.asdict()
            if k in self.oauth_param_keys})

        params["redirect_uri"]  = self.auth_config.url_for_redirect
        params["show_dialogue"] = self.show_dialogue
        params["response_type"] = "code"

        return _make_param_url(super().url_for_oauth, params)

    def aquire(self):
        key = _make_search_key(self.auth_config, "authorization_code")

        def factory():
            if not self.oauth_code:
                self.oauth_code = hosts.get_response(self)
            return _normalize_payload({
                "redirect_uri": self.auth_config.url_for_redirect,
                "grant_type": "authorization_code",
                "code": self.oauth_code,
                "scope": self.auth_config.scope,
                "state": self.auth_config.state})

        return _aquire_token(self, key, factory=factory)

    def __init__(self, *args, show_dialogue: bool = False, **kwds):
        super().__init__(*args, **kwds)

        # Attributes used for browser behavior.
        self.show_dialogue = show_dialogue
