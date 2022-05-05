import base64
import dataclasses
import http
import re
import time
import types
import typing

import requests
import requests.api

import spotipy.errors as errors


# Used to encode, and then decode
# the input values used to generate
# the authentication string.
AUTH_ENCODING: str = "ascii"


def auth_string(client_id: str, client_secret: str):
    """
    Generate the string used to authenticate
    API callouts.
    """

    auth = f"{client_id}:{client_secret}".encode(AUTH_ENCODING)
    return f"Basic {base64.b64encode(auth).decode(AUTH_ENCODING)}"


# The below determines any values
# that should be expected either in
# the application's environment, or
# defined by the user.
EXPECTED_CREDENTIALS = (
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "SPOTIFY_CLIENT_USERNAME",
    "SPOTIFY_REDIRECT_URI"
)

# Applicable for items above in
# `EXPECTED_CREDENTIALS`. This regex
# is used to remove/identify the
# SPOTIFY_ prefix.
EXPECTED_ENV_PREFIX = re.compile(r"^(SPOTIFY|spotify)_*")


def normalize_string(value: str):
    """
    Ensure the passed in value is
    normalized to be used as a keyword
    argument.
    """

    return EXPECTED_ENV_PREFIX.sub("", value).lower().replace("-", "_")


# Identify values in a string separated
# either by a single space or a comma.
EXPECTED_SCOPE_FORMAT = re.compile(r"\w+[, ]{1}")


@typing.overload
def normalize_scope(value: str):
    ...


@typing.overload
def normalize_scope(value: typing.Iterable[str]):
    ...


def normalize_scope(value: str):
    """
    Transform the passed value to
    something consumable by the `Spotify API`.
    """

    if isinstance(value, str):
        value = EXPECTED_SCOPE_FORMAT.split(value)
    return " ".join(value)


def token_expired(token_data: dict[str, typing.Any]):
    """
    Determines whether the current token
    has expired yet or not.
    """

    now = int(time.time())
    return (token_data["expires_at"] - now) < 60


def scope_is_subset(subset: str, scope: str):
    """
    Determines if the `subset` is
    contained in the scope `scope`.
    """

    subset = set(EXPECTED_SCOPE_FORMAT.split(subset))
    scope  = set(EXPECTED_SCOPE_FORMAT.split(scope))

    return subset <= scope


class SpotifySession(requests.Session):
    pass


@dataclasses.dataclass(slots=True)
class SpotifyCredentials:
    client_id:       str
    client_secret:   str
    redirect_url:    str
    client_username: str


def make_credentials(
    client_id: str,
    client_secret: str,
    redirect_url: str = None,
    username: str = None):
    """
    Generate a `SpotifyCredentials`
    object.
    """

    return SpotifyCredentials(client_id, client_secret, redirect_url, username)


class SessionFactory(typing.Protocol):

    @staticmethod
    def __call__(cls: type[SpotifySession]) -> types.ModuleType | SpotifySession:
        ...


def basic_session_factory(cls: type[SpotifySession]):
    if not cls:
        return requests.api
    return cls()


def make_session(
    session: SpotifySession,
    session_factory: SessionFactory = None):
    """
    Generate a `SpotifySession` object.

    if `session` is `None` or a type of `Session`,
    build new session object using the
    `session_factory`.
    """

    if not session_factory:
        session_factory = basic_session_factory

    # We assume if no active session
    # is passed, that it is either
    # a `Session` type or `None`.
    # Consequently, we then call the factory.
    if not isinstance(session, SpotifySession):
        session = session_factory(session)

    return session


def handle_http_error(error: requests.HTTPError):
    """
    Handle an HTTP exception.
    """
    resp   = error.response
    status = http.HTTPStatus(resp.status_code)

    try:
        payload = resp.json()
    except ValueError:
        error_message     = resp.txt or None
        error_description = None
    else:
        error_message     = payload["error"]
        error_description = payload["error_description"]

    raise errors.SpotifyOAuthError(error_message,
        reason=error_description,
        code=resp.status_code,
        http_status=status.description)
