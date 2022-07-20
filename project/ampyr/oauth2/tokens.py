"""
Helper functions and utilities for token data.
"""

# --------------------------------------------- #
# Token Data Management. Described below should
# be used for the manipulation of token metadata.
# For example, detecting if tokens are expired or
# invalid, requesting new tokens, or retrieval of
# tokens from local sources.
# --------------------------------------------- #

import base64, enum, hashlib, random, re, secrets, time, typing

from ampyr import typedefs as td
from ampyr.oauth2 import configs

EXPIRATION_THRESHOLD = 60
"""
Amount of time in seconds allowed as a buffer
between 'expired' and 'valid'.
"""

CHALLENGE_ENCODING = "UTF-8"
"""
Used to determine what encoding to use when
generating the code challenge request.
"""

AUTH_ENCODING = "ASCII"
"""
Used to encode, and then decode, the input values
for generating the authentication string.
"""


class TokenState(enum.Enum):
    """
    State of an OAuth token. Determines how to
    handle the current token.
    """

    ISVALID = enum.auto()
    """Token is good. No action required."""

    EXPIRED = enum.auto()
    """Token is bad. Needs to be refreshed."""

    INVALID = enum.auto()
    """Token is bad. Something went wrong."""


def validate(data: td.OptTokenMetaData, *, scope: td.OptString = None):
    """
    Determines the state of a given token. See
    the `TokenState` enum mapping for available
    responses.
    """

    # No token is a bad token.
    if data is None:
        return TokenState.INVALID

    # Can't continue with comparison without a
    # scope.
    if "scope" not in data:
        return TokenState.INVALID

    data_scope = str(data["scope"])
    scope      = str(scope or data_scope)

    # Ensures the scope captured in the token
    # data matches the given scope.
    if not scope_is_subset(scope, data_scope):
        return TokenState.INVALID

    if isexpired(data):
        return TokenState.EXPIRED

    return TokenState.ISVALID


def isexpired(data: td.TokenMetaData):
    """
    Determines whether or not the current token
    has expired yet or not.
    """

    now = int(time.time())
    return (data["expires_at"] - now) < EXPIRATION_THRESHOLD


@typing.overload
def set_expires(data: td.TokenMetaData):
    ...


@typing.overload
def set_expires(data: td.TokenMetaData, expires_at: int):
    ...


def set_expires(data: td.TokenMetaData, expires_at: td.Optional[int] = None):
    """
    Sets the time the given token will expire on.
    If no expires_at value is passed, will
    attempt to gain the expiration time from the
    token metadata; otherwise default assumption
    is in an hour from the current time.
    """

    # If "expires_at" given, set the value as
    # such and bail.
    if expires_at:
        data["expires_at"] = expires_at
        return

    now = int(time.time())

    # Fist default. Set expire time to the passed
    # "expires_in" value after current time.
    if hasattr(data, "expires_in"):
        data["expires_at"] = now + data["expires_in"]
        return

    # Final default. Set expire time to an hour
    # after current time.
    data["expires_at"] = now + 3600


def make_authstring(config: configs.AuthConfig):
    """
    Generate the string used to authenticate API
    callouts.
    """

    auth = (":".join([
        config.client_id, config.client_secret])).encode(AUTH_ENCODING)
    return f"Basic {base64.b64encode(auth).decode(AUTH_ENCODING)}"


def make_challenge(config: configs.AuthConfig):
    """
    Generates a url-safe, base64 encoded, number.
    String's output is determined by its input.
    """

    verif = config.code_verifier

    digest = hashlib.sha256(verif.encode(CHALLENGE_ENCODING))
    rawb64 = base64.urlsafe_b64encode(digest.digest())
    return rawb64.decode(CHALLENGE_ENCODING).replace("=", "")


def make_headers(config: configs.AuthConfig):
    """
    Generates a mapping of request headers.
    """

    return {"Authorization": make_authstring(config)}


def make_verifier():
    """
    Generates a url-safe, base64 encoded, number.
    String is pseudo-random.
    """

    return secrets.token_urlsafe(random.randint(33, 96))


# --------------------------------------------- #
# Authentication Scope Management. Here are a
# list of functions/procedures expected to assist
# in manipulation of scopes and scope strings.
#
# Scope is an Auth2.0 mechanism that limits the
# access an application has to a user's
# account. An application can request a single or
# multiple scopes where then the user must
# consent before access is granted, or rejected.
# --------------------------------------------- #

# Identify values in a string separated either by
# a single space or a comma.
EXPECTED_SCOPE_FORMAT = re.compile(r"\w+[, ]{1}")
"""Pattern dictating compound scope format."""


def normalize_scope(scope: td.AuthScope, *, join_char: td.OptString = None):
    """
    Transform the given value into something
    consumable by an authorization server.

    The given scope is expected to be either a
    word, a series of comma separated words, or
    a sequence of words.
    """

    if isinstance(scope, str):
        scope = EXPECTED_SCOPE_FORMAT.split(scope)
    return (join_char or " ").join(scope)


def scope_is_subset(first: td.OptString, second: td.OptString = None):
    """
    Compares two given scopes to determine if one
    is contained in the other.
    """

    # If either of the given values are `None`,
    # check to see if they both are.
    if None in (first, second):
        return first == second

    # Takes a string against the expected scope
    # pattern and returns a set of it's values.
    split = lambda scope: set(EXPECTED_SCOPE_FORMAT.split(scope))

    first_set, second_set = [
        split(i) for i in (first, second)]
    return any([first_set <= second_set, second_set <= first_set])
