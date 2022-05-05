import abc
import os
import typing

import requests

from spotipy.oauth import utils
from spotipy.oauth import cache
from spotipy.oauth.auth import base


class SpotifyAuthFlow(typing.Protocol):

    def get_access_token(self) -> str:
        """
        Retrieves an access token from the `Spotify API`
        """


class BaseAuthFlow(base.SpotifyBaseAuthenticator, abc.ABC):

        def __init__(self, client_id: str, client_secret: str, *,
            proxies: dict[str, str] = None,
            session: utils.SpotifySession = None,
            session_factory: utils.SessionFactory = None,
            timeout: float | tuple[float, ...] = None,
            cache_cls: type[cache.SpotifyCacheHandler] = None,
            cache_params: dict[str, typing.Any] = None):

            super(BaseAuthFlow, self).__init__(session, session_factory=session_factory)

            # Set the client_id and client_secret.
            self.credentials.client_id     = client_id
            self.credentials.client_secret = client_secret

            # Apply additional values to the
            # internal session.
            self.session.proxies = proxies

            # Homeless attributes.
            self.timeout = timeout

            if not cache_cls:
                cache_cls = cache.FileCacheHandler
            self.cache_cls    = cache_cls
            self.cache_params = cache_params

        @abc.abstractmethod
        def get_access_token(self) -> str:
            """
            Retrieves an access token from the `Spotify API`
            """


class ClientCredentialsFlow(BaseAuthFlow):
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
        with cache.SpotifyCachePool(
            self.cache_cls, hkwds=self.cache_params) as cpool:

            cursor     = cpool.new()
            token_data = cursor.find_token_data()

            # If a valid token is found,
            # return that value.
            if token_data and not utils.token_expired(token_data):
                return token_data["access_token"]

            # Build a request using the
            # internal session.
            auth = utils.auth_string(
                self.credentials.client_id,
                self.credentials.client_secret)

            resp = self.session.post(
                self.token_url,
                data={"grant_type": "client_credentials"},
                headers={"Authorization": f"Basic {auth}"}
            )

            # Test if there was an issue
            # from the callout, handle any
            # subsequent errors.
            try:
                resp.raise_for_status()
            except requests.HTTPError as error:
                utils.handle_http_error(error)
            else:
                token_data = resp.json()
                utils.set_expires_at(token_data)

            cursor.save_token_data(token_data)
            return token_data["access_token"]


class AuthorizationFlow(BaseAuthFlow):
    """
    The Authorization Auth Flow is used in
    app-based authentication.
    Provided a scope, this flow grants
    a wider range of access to the `Spotify API`.

    This `AuthFlow` does require user interaction.
    """

    def __init__(self, client_id: str, client_secret: str, *,
        user_id: str = None,
        proxies: dict[str, str] = None,
        session: utils.SpotifySession = None,
        session_factory: utils.SessionFactory = None,
        timeout: float | tuple[float, ...] = None,
        cache_cls: type[cache.SpotifyCacheHandler] = None,
        cache_params: dict[str, typing.Any] = None,
        cache_path: os.PathLike = None,
        state: str = None,
        scope: str | typing.Iterable[str] = None,
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
        self.scope = utils.normalize_scope(scope or "")
        self.state = state

        # Attributes used for browser
        # behavior.
        self.show_dialogue = show_dialogue
        self.open_browser  = open_browser
