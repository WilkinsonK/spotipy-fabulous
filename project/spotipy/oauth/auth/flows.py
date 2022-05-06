"""
auth/flows.py

In this module there are defined a series of objects
that subclass from the `BaseAuthFlow` abstraction. See
base.py for reference.

These objects-- "Auth Flows"-- are designed to obtain
access to Spotify's API by retrieving a token. The
`Spotify API` utilizes OAuth2.0 and it's practices,
the Auth Flows in this module represent those different
practices.

Current available Auth Flows:
* ClientCredentialsFlow
* AuthorizationFlow
* PKCEFlow

NOTE: Because "Implicit Grant" is not a recommened
authentication flow, per `Spotify API` documentation,
there is no object defined for it's purpose.
"""

import os, typing
import urllib.parse as urlparse

from spotipy import oauth
from spotipy.oauth import cache
from spotipy.oauth.auth import scopes, base, host, sessions, tokens


def authorize_url(base_url: str, params: dict[str, typing.Any]):
    """
    Generate the url used to
    request authorization.
    """

    params = oauth.normalize_payload(params)
    return "?".join([base_url, urlparse.urlencode(params)])


class ClientCredentialsFlow(base.BaseAuthFlow):
    """
    The Client Credentials Auth Flow is used in
    server-to-server authentication.
    Only endpoints taht do not access user
    information can be accessed. This limits any
    callouts using this `AuthFlow` to any
    non-scope related routes.

    This `AuthFlow` does not require any user
    interaction.
    """

    def get_access_token(self) -> str:

        def factory():
            return {"grant_type": "client_credentials"}

        return tokens.find_token_data(self, factory)["access_token"] #type: ignore[index]


class AuthorizationFlow(base.BaseAuthFlow):
    """
    The Authorization Auth Flow is used in
    app-based authentication primarily.
    Provided a scope, this flow grants
    a wider range of access to the `Spotify API`.

    This `AuthFlow` does require user interaction.
    """

    def __init__(self, client_id: str, client_secret: str, *,
        user_id: str = None,
        redirect_url: str = None,
        proxies: dict[str, str] = None,
        session: type[sessions.SpotifySession] = None,
        session_factory: sessions.SessionFactory = None,
        timeout: float | tuple[float, ...] | None = None,
        cache_cls: type[cache.SpotifyCacheHandler] = None,
        cache_params: dict[str, typing.Any] = None,
        cache_path: os.PathLike = None,
        state: str = None,
        scope: str | typing.Iterable[str] | None = None,
        show_dialogue: bool = False,
        open_browser: bool = True):

        if not cache_params:
            cache_params = {}
        if not cache_cls:
            cache_cls = cache.FileCacheHandler

        if cache_cls in (cache.FileCacheHandler, cache.ShelfCacheHandler):
            cache_params.update({
                "user_id": user_id,
                "path": cache_path})

        super(AuthorizationFlow, self).__init__(
            client_id,
            client_secret,
            proxies=proxies,
            session=session,
            session_factory=session_factory,
            timeout=timeout,
            cache_cls=cache_cls,
            cache_params=cache_params)

        # Auth specific attributes.
        self.credentials.client_username = user_id
        self.credentials.redirect_url    = redirect_url

        self.credentials.scope = scopes.normalize_scope(scope or "")
        self.credentials.state = state

        # Attributes used for browser
        # behavior.
        self.show_dialogue = show_dialogue
        self.open_browser  = open_browser

    @property
    def authorize_url(self):
        payload = {
            "client_id": self.credentials.client_id,
            "redirect_uri": self.credentials.redirect_url,
            "scope": self.credentials.scope,
            "state": self.credentials.state,
            "show_dialogue": self.show_dialogue,
            "response_type": "code"
        }
        return authorize_url(super().authorize_url, payload)

    def get_access_token(self, status_code: int = None) -> str:
        
        def factory(code=status_code):
            if not code:
                code = host.get_auth_response(self)
            return oauth.normalize_payload({
                "redirect_uri": self.credentials.redirect_url,
                "grant_type": "authorization_code",
                "code": code,
                "scope": self.credentials.scope,
                "state": self.credentials.state})

        return tokens.find_token_data(self, factory)["access_token"] #type: ignore[index]


class PKCEFlow(base.BaseAuthFlow):
    """
    Proof Key for Code Exchange

    This Auth Flow enables `user` and `non-user`
    endpoints.

    When this Auth Flow requests an access
    token for the first time, the user is prompted
    for approval.

    This is the recommended Auth Flow for
    moble/desktop applications.
    """

    def __init__(self, client_id: str, user_id: str, *,
        redirect_url: str = None,
        proxies: dict[str, str] = None,
        session: type[sessions.SpotifySession] = None,
        session_factory: sessions.SessionFactory = None,
        timeout: float | tuple[float, ...] | None = None,
        cache_cls: type[cache.SpotifyCacheHandler] = None,
        cache_params: dict[str, typing.Any] = None,
        cache_path: os.PathLike = None,
        state: str = None,
        scope: str | typing.Iterable[str] | None = None,
        open_browser: bool = True):

        if not cache_params:
            cache_params = {}
        if not cache_cls:
            cache_cls = cache.FileCacheHandler

        if cache_cls in (cache.FileCacheHandler, cache.ShelfCacheHandler):
            cache_params.update({
                "user_id": user_id,
                "path": cache_path
            })

        super(PKCEFlow, self).__init__(
            client_id,
            "",
            proxies=proxies,
            session=session,
            session_factory=session_factory,
            timeout=timeout,
            cache_cls=cache_cls,
            cache_params=cache_params)

        # Auth specific attributes.
        self.credentials.client_username = user_id
        self.credentials.redirect_url    = redirect_url

        self.credentials.scope = scopes.normalize_scope(scope or "")
        self.credentials.state = state

        verifier = tokens.make_code_verifier()
        self.credentials.code_verifier  = verifier
        self.credentials.code_challenge = tokens.make_code_challenge(verifier)

        # Attributes used for browser
        # behavior.
        self.open_browser = open_browser

    @property
    def authorize_url(self):
        payload = {
            "client_id": self.credentials.client_id,
            "redirect_uri": self.credentials.redirect_url,
            "code_challenge": self.credentials.code_challenge,
            "scope": self.credentials.scope,
            "state": self.credentials.state,
            "code_challenge_method": "S256",
            "response_type": "code"
        }
        return authorize_url(super().authorize_url, payload)

    def get_access_token(self, status_code: int = None) -> str:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        def factory(code=status_code):
            if not code:
                code = host.get_auth_response(self)
            return oauth.normalize_payload({
                "redirect_uri": self.credentials.redirect_url,
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.credentials.client_id,
                "code_verifier": self.credentials.code_verifier})

        return tokens.find_token_data(self, factory, headers)["access_token"] #type: ignore[index]
