"""
Listed below are various exceptions used for this
package.
"""

import http
from typing import Optional


class SpotifyException(Exception):
    """
    Raised in the event of any errors related to
    the `Spotify Web API`.
    """


class SpotifyHttpError(SpotifyException):
    """
    Raised in the event of any HTTP related
    errors from the `Spotify Web API`.
    """

    status: http.HTTPStatus = http.HTTPStatus(500)
    """Response code from `Spotify Web API`."""

    def __init__(self, *values, status: Optional[http.HTTPStatus] = None):
        super().__init__(self, *values)

        # Custom http attributes.
        if status:
            self.status = status

    def __str__(self):
        return "{}: {}".format(self.status.value, super().__str__())


class SpotifyUnauthorizedError(SpotifyHttpError):
    """
    Raised in the event of some transaction is
    attempted outside what the client is allowed.
    """

    status: http.HTTPStatus = http.HTTPStatus(401)


class SpotifyNotFoundError(SpotifyHttpError):
    """
    Raised in the event of some transaction
    fails because a resource could not be found.
    """

    status: http.HTTPStatus = http.HTTPStatus(404)


class SpotifyInternalError(SpotifyHttpError):
    """
    Raised in the event the `Spotify Web API`
    fails internally.
    """

    status: http.HTTPStatus = http.HTTPStatus(500)


class SpotifyNotImplementedError(SpotifyHttpError):
    """
    Raised in the event of some transaction
    failing because the target does not support
    the request method.
    """

    status: http.HTTPStatus = http.HTTPStatus(501)


class OAuth2Exception(Exception):
    """
    Raised in the event of any errors related to
    `OAuth2.0` and authentication events.
    """


class OAuth2HttpError(OAuth2Exception, SpotifyHttpError):
    """
    Raised in the event of any errors related to
    `OAuth2.0` and HTTP events.
    """


class OAuth2BadStateError(OAuth2HttpError):
    """
    Raised in the event where the state returned
    from a token request is not the same as
    what was expected.
    """


class OAuthValueError(OAuth2Exception):
    """
    Raised in the event of some value either
    being missing or invalid.
    """
