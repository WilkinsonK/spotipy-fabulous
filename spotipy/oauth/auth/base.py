import spotipy.oauth.utils as utils


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
