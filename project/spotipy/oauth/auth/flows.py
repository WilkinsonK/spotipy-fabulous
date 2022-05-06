import abc
import http
import os
import typing

import urllib.parse as urlparse
import webbrowser

import requests

from spotipy import errors
from spotipy.oauth import cache, server, utils
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

            if not session:
                session = utils.SpotifySession

            super(BaseAuthFlow, self).__init__(session, session_factory=session_factory)

            # Set the client_id and client_secret.
            self.credentials.client_id     = client_id
            self.credentials.client_secret = client_secret

            # Apply additional values to the
            # internal session.
            self.session.proxies = proxies
            self.session.verify  = True

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

        def validate_token(self, token_data: utils.TokenData) -> bool:
            """
            Ensure the given token is valid.
            """

            if not utils.token_data_valid(token_data):
                return False

            if "scope" not in token_data:
                return False

            scope  = self.credentials.scope
            if not utils.scope_is_subset(token_data, scope):
                return False

            return True


def get_token_data(auth_flow: BaseAuthFlow, payload: dict[str, typing.Any]):
    """
    Sends an outbound auth call requesting
    for a token.
    """

    # Build a request using the
    # internal session.
    auth = utils.auth_string(
        auth_flow.credentials.client_id,
        auth_flow.credentials.client_secret)

    resp = auth_flow.session.post(
        auth_flow.token_url,
        data=payload,
        headers={"Authorization": auth})

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

        return token_data


def get_host_info(result: urlparse.ParseResult):
    """
    Retrieves host and port information
    from the url `ParseResult`.
    """

    return result.netloc.split(":")[0], result.port


# Represents list of expected aliases
# for the localhost.
LOCAL_HOST_NAMES = ("127.0.0.1", "localhost")


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
            if not self.validate_token(token_data):
                payload    = {"grant_type": "client_credentials"}
                token_data = get_token_data(self, payload)
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
        redirect_url: str = None,
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
        self.credentials.client_username = user_id
        self.credentials.redirect_url    = redirect_url

        self.credentials.scope = utils.normalize_scope(scope or "")
        self.credentials.state = state

        # Attributes used for browser
        # behavior.
        self.show_dialogue = show_dialogue
        self.open_browser  = open_browser

    @property
    def authorize_url(self):
        payload = utils.normalize_payload({
            "client_id": self.credentials.client_id,
            "redirect_uri": self.credentials.redirect_url,
            "scope": self.credentials.scope,
            "state": self.credentials.state,
            "show_dialogue": self.show_dialogue,
            "response_type": "code"
        })

        params = urlparse.urlencode(payload)
        return "?".join([super().authorize_url, params])

    def get_access_token(self, status_code: http.HTTPStatus = None) -> str:
        with cache.SpotifyCachePool(
            self.cache_cls, hkwds=self.cache_params) as cpool:

            cursor     = cpool.new()
            token_data = cursor.find_token_data()

            # If a valid token is found,
            # return that value.
            if not utils.token_data_valid(token_data):
                if not status_code:
                    status_code = self.get_auth_response()

                payload = utils.normalize_payload({
                    "code": status_code,
                    "redirect_uri": self.credentials.redirect_url,
                    "grant_type": "authorization_code",
                    "scope": self.credentials.scope,
                    "state": self.credentials.state
                })
                token_data = get_token_data(self, payload)
                cursor.save_token_data(token_data)

            return token_data["access_token"]

    def get_auth_response(self):
        """
        Requests authentication from the
        user. This requires interaction
        with a web browser.
        """

        result     = urlparse.urlparse(self.credentials.redirect_url)
        host, port = get_host_info(result)

        # If we anticipate an HTTP server
        # on the local machine, create that
        # server.
        if host in LOCAL_HOST_NAMES and result.scheme == "http":
            port = port or 8080
            return self.local_auth_response(port)

    def local_auth_response(self, port: int):
        """
        Attempt to get authentication
        from the user's browser.
        """
        serv  = server.make_server(port)
        creds = self.credentials

        webbrowser.open(self.authorize_url)
        serv.handle_request()

        if serv.error:
            raise serv.error

        # Ensure the state received
        # matches the state sent.
        if creds.state and (serv.state != creds.state):
            status = http.HTTPStatus(500)
            raise errors.SpotifyStateError("",
                reason=status.name,
                code=status.value,
                http_status=status.description,
                local_state=creds.state,
                remote_state=serv.state)

        if serv.auth_code:
            return serv.auth_code

        # If failure to obtain an auth code,
        # throw an auth error.
        status = http.HTTPStatus(500)
        raise errors.SpotifyOAuthError(
            "Server listening on localhost was never accessed!",
            reason=status.description,
            code=status.value,
            http_status=status.phrase)
