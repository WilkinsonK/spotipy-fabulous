import base64
import re


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


def normalize(value: str):
    """
    Ensure the passed in value is
    normalized to be used as a keyword
    argument.
    """

    return EXPECTED_ENV_PREFIX.sub("", value).lower().replace("-", "_")
