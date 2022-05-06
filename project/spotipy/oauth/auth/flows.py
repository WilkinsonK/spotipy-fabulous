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

        # Including this here to
        # signify this needful.
        # all other `AuthFlow`s should
        # be expected to have this attr.
        token_payload: dict[str, str]

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


def _get_token_data(auth_flow: BaseAuthFlow, payload: dict[str, typing.Any]):
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


class TokenPayloadFactory(typing.Protocol):
    """
    A useful pre-get_token_data hook.
    Intended for the user to manipulate
    the request payload before the
    callout.
    """

    @staticmethod
    def __call__() -> dict[str, typing.Any]:
        ...


def basic_payload_factory():
    """
    Returns a dummy payload with no data.
    """

    return {}


def get_token_data(
    auth_flow: BaseAuthFlow,
    cursor: cache.SpotifyCacheHandler,
    payload_factory: TokenPayloadFactory = None):
    """
    Retrieves an access token from the
    `Spotify API`. This function first checks,
    and validates for token data that
    may have been previously cached.
    """

    ts = utils.TokenState

    # Initial lookup for a token from
    # the `auth_flow`'s cache handler.
    token_data = cursor.find_token_data()

    # Validate the token data found.
    # not unlike for parking...
    scope        = auth_flow.credentials.scope
    token_state  = utils.validate_token(token_data, auth_scope=scope)

    if token_state is ts.VALID:
        return token_data

    if token_state is ts.REFRESH:
        payload = {
            "refresh_token": token_data["refresh_token"],
            "grant_type": "refresh_token"
        }
    else:
        if not payload_factory:
            payload_factory = basic_payload_factory
        payload = payload_factory()

    # Token either required a refresh
    # or was invalid. Get new token data
    # and try again.
    token_data = _get_token_data(auth_flow, payload)
    if "scope" not in token_data:
        token_data["scope"] = scope
    cursor.save_token_data(token_data)

    return get_token_data(auth_flow, cursor, payload_factory)


def find_token_data(
    auth_flow: BaseAuthFlow,
    factory: TokenPayloadFactory) -> utils.TokenData:
    """
    Find valid auth token data.
    """

    # Args required to open the cache
    # pool.
    hcls, hkwds = auth_flow.cache_cls, auth_flow.cache_params

    with cache.SpotifyCachePool(hcls, hkwds=hkwds) as cpool:
        curs = cpool.new()
        return get_token_data(auth_flow, curs, factory)


def get_host_info(result: urlparse.ParseResult):
    """
    Retrieves host and port information
    from the url `ParseResult`.
    """

    return result.netloc.split(":")[0], result.port


# Represents list of expected aliases
# for the localhost.
LOCAL_HOST_NAMES = ("127.0.0.1", "localhost")


def local_auth_response(auth_flow: BaseAuthFlow, port: int):
    """
    Attempt to get authentication
    from the user's browser.
    """

    serv  = server.make_server(port)
    creds = auth_flow.credentials

    webbrowser.open(auth_flow.authorize_url)
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


def get_auth_response(auth_flow: BaseAuthFlow):
    """
    Requests authentication from the
    user. This requires interaction
    with a web browser.
    """

    result     = urlparse.urlparse(auth_flow.credentials.redirect_url)
    host, port = get_host_info(result)

    # If we anticipate an HTTP server
    # on the local machine, create that
    # server.
    if host in LOCAL_HOST_NAMES and result.scheme == "http":
        port = port or 8080
        return local_auth_response(auth_flow, port)


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

        def factory():
            return {"grant_type": "client_credentials"}

        return find_token_data(self, factory)["access_token"]


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

    def get_access_token(self, status_code: int = None) -> str:
        
        def factory(code=status_code):
            if not code:
                code = get_auth_response(self)
            return utils.normalize_payload({
                "redirect_uri": self.credentials.redirect_url,
                "grant_type": "authorization_code",
                "code": code,
                "scope": self.credentials.scope,
                "state": self.credentials.state
            })

        return find_token_data(self, factory)["access_token"]
