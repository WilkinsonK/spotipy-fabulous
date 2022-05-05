import spotipy.oauth.auth.base as base
import spotipy.oauth.utils as utils


class BaseAuthFlow(base.SpotifyBaseAuthenticator):

    def __init__(self,
        client_id: str = None,
        client_secret: str = None,
        *,
        proxies: dict[str, str] = None,
        session: utils.SpotifySession = None,
        session_factory: utils.SessionFactory = None,
        timeout: float | tuple[float, ...] = None):

        super(BaseAuthFlow, self).__init__(session, session_factory=session_factory)

        # Set the client_id and client_secret.
        self.credentials.client_id     = client_id
        self.credentials.client_secret = client_secret

        # Apply additional values to the
        # internal session.
        self.session.proxies = proxies

        # Homeless attributes.
        self.timeout = timeout
