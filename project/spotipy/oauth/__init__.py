"""
spotify/oauth

In this module there are defined a series of objects
that subclass from the `BaseAuthFlow` abstraction. See
base.py for reference.

These objects-- "Auth Flows"-- are designed to obtain
access to Spotify's API by retrieving a token. The
`Spotify API` utilizes OAuth2.0 and it's practices,
the Auth Flows in this module represent those different
practices.

Current available Auth Flows:
* ClientCredentialsFlow
* AuthorizationFlow
* PKCEFlow

NOTE: Because "Implicit Grant" is not a recommened
authentication flow, per `Spotify API` documentation,
there is no object defined for it's purpose.
"""

import http, re, typing

import requests

from spotipy import errors


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


TokenDataType = dict[str, typing.Any]
TokenData     = typing.TypeVar("TokenData", bound=TokenDataType)
"""Mapping of data from access request."""

OptionalTokenData = typing.Optional[TokenData]


# Represents the expected form
# a callable should take to qualify
# for use in filtering.
T             = typing.TypeVar("T")
ConditionType = typing.Callable[[T | None], bool]
Condition     = typing.TypeVar("Condition", bound=ConditionType)
"""Callable, given an object, which returns a boolean."""


def normalize_payload(payload: dict[str, typing.Any], *,
    condition: Condition = None):
    """
    Filter out any fields in the payload
    that do not meet the condition.

    default behavior is "object is truthy"
    """

    func = condition or (lambda o: bool(o))
    return {k:v for k,v in payload.items() if func(v)}


def handle_http_error(error: requests.HTTPError):
    """
    Handle an HTTP exception.
    """
    resp   = error.response
    status = http.HTTPStatus(resp.status_code)

    try:
        payload = resp.json()
    except ValueError:
        error_message     = resp.text or None
        error_description = None
    else:
        error_message     = payload.get("error", None)
        error_description = payload.get("error_description", None)

    raise errors.SpotifyOAuthError(
        str(error_message),
        reason=error_description or status.description,
        code=status.value,
        http_status=status.phrase)


from spotipy.oauth.auth import ClientCredentialsFlow, \
    AuthorizationFlow, PKCEFlow
