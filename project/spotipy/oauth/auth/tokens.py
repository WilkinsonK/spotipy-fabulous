"""
auth/tokens.py

Token tools for manipulating token data.
"""

import base64, enum, hashlib, random, secrets, time, typing

import requests

from spotipy import oauth
from spotipy.oauth import cache
from spotipy.oauth.auth import scopes, base


def token_expired(token_data: oauth.TokenData):
    """
    Determines whether the current token
    has expired yet or not.
    """

    now = int(time.time())
    return (token_data["expires_at"] - now) < 60


def set_expires_at(token_data: oauth.TokenData):
    """
    Sets the time the current token
    will expire on.
    """

    now = int(time.time())
    token_data["expires_at"] = now + token_data["expires_in"]


class TokenState(enum.Enum):
    VALID   = enum.auto()
    REFRESH = enum.auto()
    INVALID = enum.auto()


def validate_token(token_data: oauth.TokenData, *,
    auth_scope: str = None) -> TokenState:
    """
    Determines the state of a given token.
    See the `TokenState` enum mapping for
    available responses.

    * `VALID`:   current token data is OK.
    * `REFRESH`: current token needs renewed.
    * `INVALID`: something wrong with the current token.
    """

    # No token is a bad token.
    if token_data is None:
        return TokenState.INVALID

    # Can't continue comparison
    # without a scope.
    if "scope" not in token_data:
        return TokenState.INVALID

    scope = token_data["scope"]
    if not auth_scope:
        auth_scope = scope

    # Ensures the scope captured
    # in token data matches the
    # given scope.
    if not scopes.scope_is_subset(scope, auth_scope):
        return TokenState.INVALID

    if token_expired(token_data):
        return TokenState.REFRESH

    return TokenState.VALID


def _get_token_data(
    auth_flow: base.BaseAuthFlow,
    payload: dict[str, typing.Any],
    headers: dict[str, str]):
    """
    Sends an outbound auth call requesting
    for a token.
    """

    resp = auth_flow.session.post(
        auth_flow.token_url,
        data=payload,
        headers=headers)

    # Test if there was an issue
    # from the callout, handle any
    # subsequent errors.
    try:
        resp.raise_for_status()
    except requests.HTTPError as error:
        oauth.handle_http_error(error)
    else:
        token_data = resp.json()
        set_expires_at(token_data)

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
    auth_flow: base.BaseAuthFlow,
    cursor: cache.SpotifyCacheHandler,
    headers: dict[str, str],
    payload_factory: TokenPayloadFactory = None):
    """
    Retrieves an access token from the
    `Spotify API`. This function first checks,
    and validates for token data that
    may have been previously cached.
    """

    # Initial lookup for a token from
    # the `auth_flow`'s cache handler.
    token_data = cursor.find_token_data()

    # Validate the token data found.
    # not unlike for parking...
    scope        = auth_flow.credentials.scope
    token_state  = validate_token(token_data, auth_scope=scope)

    if token_state is TokenState.VALID:
        return token_data

    if token_state is TokenState.REFRESH:
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
    token_data = _get_token_data(auth_flow, payload, headers)
    if "scope" not in token_data:
        token_data["scope"] = scope
    cursor.save_token_data(token_data)

    return get_token_data(auth_flow, cursor, headers, payload_factory)


def find_token_data(
    auth_flow: base.BaseAuthFlow,
    factory: TokenPayloadFactory,
    headers: dict[str, str] = None) -> oauth.TokenData:
    """
    Find valid auth token data. This function
    will first check for any cached data; in the
    event that it does not, make a callout to
    Spotify's API.

    * auth_flow: the Authorization Flow object which
    represents the Authorization strategy.
    """

    # Args required to open the cache
    # pool.
    hcls, hkwds = auth_flow.cache_cls, auth_flow.cache_params

    # Get default mapping based on
    # the given Auth Flow.
    if not headers:
        headers = make_headers(auth_flow)

    with cache.SpotifyCachePool(hcls, hkwds=hkwds) as cpool:
        curs = cpool.new()
        return get_token_data(auth_flow, curs, headers, factory)


def make_headers(auth_flow: base.BaseAuthFlow):
    """
    Generates a mapping of request headers.
    """

    auth = make_auth_string(
        auth_flow.credentials.client_id,
        auth_flow.credentials.client_secret)
    return {"Authorization": auth}


def make_code_verifier():
    """
    Generates a url-safe, base64 encoded, number.
    String is pseudo-random.
    """

    return secrets.token_urlsafe(random.randint(33, 96))


# Used to determine what
# encoding to use when generating
# the code challenge digest.
CHALLENGE_ENCODING = "UTF-8"


def make_code_challenge(verifier: str):
    """
    Generates a url-safe, base64 encoded, number.
    String's output is determined by its input.
    """

    digest = hashlib.sha256(verifier.encode(CHALLENGE_ENCODING))
    raw    = base64.urlsafe_b64encode(digest.digest())
    return raw.decode(CHALLENGE_ENCODING).replace("=", "")


# Used to encode, and then decode
# the input values used to generate
# the authentication string.
AUTH_ENCODING: str = "ascii"


def make_auth_string(client_id: str, client_secret: str):
    """
    Generate the string used to authenticate
    API callouts.
    """

    auth = f"{client_id}:{client_secret}".encode(AUTH_ENCODING)
    return f"Basic {base64.b64encode(auth).decode(AUTH_ENCODING)}"
