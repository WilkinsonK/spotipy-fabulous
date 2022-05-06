import abc
import typing

from spotipy.oauth import utils, cache


class SpotifyBaseAuthenticator:
    """
    Handles the authorization/access between
    clients and the `Spotify API`.
    """

    __oauth_token_url:     str = "https://accounts.spotify.com/api/token"
    __oauth_authorize_url: str = "https://accounts.spotify.com/authorize"

    def __init__(self,
        session: utils.SpotifySession, *,
        session_factory: utils.SessionFactory = None):
        """Create new Authenticator object."""

        self._session     = utils.make_session(session, session_factory)
        self._credentials = utils.make_credentials(None, None)

    def __del__(self):
        if hasattr(self._session, "close"):
            self._session.close()

    @property
    def session(self):
        return self._session

    @property
    def credentials(self):
        return self._credentials

    @property
    def token_url(self):
        return self.__oauth_token_url

    @property
    def authorize_url(self):
        return self.__oauth_authorize_url


class SpotifyAuthFlow(typing.Protocol):

    def get_access_token(self) -> str:
        """
        Retrieves an access token from the `Spotify API`
        """


class BaseAuthFlow(SpotifyBaseAuthenticator, abc.ABC):

        # Including this here to
        # signify this needful.
        # all other `AuthFlow`s should
        # be expected to have this attr.

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
