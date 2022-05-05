import abc
import typing

import spotipy.oauth.auth.base as base
import spotipy.oauth.utils as utils


class SpotifyAuthFlow(typing.Protocol):

    def get_access_token(self) -> str:
        """
        Retrieves an access token from the `Spotify API`
        """


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


class AuthorizationFlow(BaseAuthFlow):
    """
    The Authorization Auth Flow is used in
    app-based authentication.
    Provided a scope, this flow grants
    a wider range of access to the `Spotify API`.

    This `AuthFlow` does require user interaction.
    """
