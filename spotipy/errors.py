from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ExceptionValues:
    message: str


@dataclass
class HttpExceptionValues(ExceptionValues):
    http_status: str
    code:        int

    # Optionals
    reason:  str            = field(default=None)
    headers: dict[str, Any] = field(default_factory={})


@dataclass
class OAuthExceptionValues(ExceptionValues):
    error:             str = field(default=None)
    error_description: str = field(default=None)


@dataclass
class StateExceptionValues(OAuthExceptionValues):
    local_state:  str = field(default=None)
    remote_state: str = field(default=None)


class SpotifyException(Exception):
    """
    Raised in the event of any errors
    related to the `Spotify API`.
    """

    template:   str                   = "{message}"
    values_cls: type[ExceptionValues] = ExceptionValues

    def __init__(self, message: str, *,
        template: str = None,
        values_cls: type[ExceptionValues] = None,
        **kwargs):

        if template:
            self.template = template

        if not values_cls:
            values_cls = self.values_cls
        self.values = values_cls(message, **kwargs)

    def __str__(self):
        return self.template.format(**asdict(self.values))


class SpotifyHttpError(SpotifyException):
    """
    Raised in the event of any HTTP related
    errors from the `Spotify API`.
    """

    template   = (
        "http_status: {http_status} code: {code}; {message} reason: {reason}")
    values_cls = HttpExceptionValues


class SpotifyAuthException(SpotifyException):
    """
    Raise for authentication errors.
    """


class SpotifyOAuthError(SpotifyAuthException):
    """
    Raised for errors during OAuth authentication.
    """

    template   = "{error}; {error_description}: {message}"
    values_cls = OAuthExceptionValues


class SpotifyStateError(SpotifyOAuthError):
    """
    Raised when the state sent differs from the
    state recieved.
    """

    template   = (
        SpotifyOAuthError.template +
        "\n\texpected {local_state} but recieved {remote_state}")
    values_cls = StateExceptionValues
