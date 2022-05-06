import base64
import dataclasses
import http
import os
import re
import time
import types
import typing

import requests
import requests.api

from spotipy import errors


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


# Used in the event no initial path is passed
# to `make_cache_path`. This ensures the file
# path is never empty.
DEFAULT_CACHE_PATH = ".cache"


def make_cache_path(path: os.PathLike = None, *ids: str) -> str:
    """
    Generate a path for some cache file.
    """

    if not path:
        path = DEFAULT_CACHE_PATH

    # Filter out any undefined or null
    # values. Join the remaining to
    # the filepath.
    ids = [idx for idx in ids if idx]
    if len(ids):
        path = "-".join([path, *ids])

    return path


# Represents the expected form
# a callable should take to qualify
# for use in filtering.
T             = typing.TypeVar("T")
ConditionType = typing.Callable[[T | None], bool]
Condition     = typing.TypeVar("Condition", bound=ConditionType)


def normalize_payload(payload: dict[str, typing.Any], *,
    condition: Condition = None):
    """
    Filter out any fields in the payload
    that do not meet the condition.
    """

    if not condition:
        condition = lambda o: bool(o)
    return {k:v for k,v in payload.items() if condition(v)}


"""                        #|
---- Scope Manipulation ----|
"""                        #|

TokenDataType = dict[str, typing.Any]
TokenData     = typing.TypeVar("TokenData", bound=TokenDataType)

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


def scope_is_subset(token_data: TokenData, scope: str):
    """
    Determines if the `token_data`'s
    scope is contained in the scope
    `scope`.
    """

    subset = set(EXPECTED_SCOPE_FORMAT.split(token_data["scope"]))
    scope  = set(EXPECTED_SCOPE_FORMAT.split(scope))

    return subset <= scope


"""                        #|
---- Token Manipulation ----|
"""                        #|


def token_expired(token_data: TokenData):
    """
    Determines whether the current token
    has expired yet or not.
    """

    now = int(time.time())
    return (token_data["expires_at"] - now) < 60


def token_data_valid(token_data: TokenData):
    return bool(token_data) and not token_expired(token_data)


def set_expires_at(token_data: TokenData):
    """
    Sets the time the current token
    will expire on.
    """

    now = int(time.time())
    token_data["expires_at"] = now + token_data["expires_in"]


"""                            #|
---- Credentials Management ----|
"""                            #|


@dataclasses.dataclass(slots=True)
class SpotifyCredentials:
    client_id:       str
    client_secret:   str
    redirect_url:    str
    client_username: str
    scope:           str | None = None
    state:           str | None = None


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


"""              #|
---- Sessions ----|
"""              #|


class SpotifySession(requests.Session):
    pass


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
        error_message     = payload.get("error", None)
        error_description = payload.get("error_description", None)

    raise errors.SpotifyOAuthError(error_message,
        reason=error_description or status.description,
        code=status.value,
        http_status=status.phrase)
