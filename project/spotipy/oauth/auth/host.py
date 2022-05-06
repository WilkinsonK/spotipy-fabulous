"""
auth/host.py

Host tools for retrieving an authentication
response.
"""

import http
import urllib.parse as urlparse
import webbrowser

from spotipy import errors
from spotipy.oauth import server
from spotipy.oauth.auth import base


def get_host_info(result: urlparse.ParseResult):
    """
    Retrieves host and port information
    from the url `ParseResult`.
    """

    return result.netloc.split(":")[0], result.port


# Represents list of expected aliases
# for the localhost.
LOCAL_HOST_NAMES = ("127.0.0.1", "localhost")


def local_host_response(auth_flow: base.BaseAuthFlow, port: int):
    """
    Attempt to get authentication
    from the user's browser.
    """

    serv  = server.make_server(port)
    creds = auth_flow.credentials

    webbrowser.open(auth_flow.authorize_url)
    serv.handle_request()

    if serv.error:
        raise serv.error

    # Ensure the state received
    # matches the state sent.
    if creds.state and (serv.state != creds.state):
        status = http.HTTPStatus(500)
        raise errors.SpotifyStateError("",
            reason=status.name,
            code=status.value,
            http_status=status.description,
            local_state=creds.state,
            remote_state=serv.state)

    if serv.auth_code:
        return serv.auth_code

    # If failure to obtain an auth code,
    # throw an auth error.
    status = http.HTTPStatus(500)
    raise errors.SpotifyOAuthError(
        "Server listening on localhost was never accessed!",
        reason=status.description,
        code=status.value,
        http_status=status.phrase)


def get_auth_response(auth_flow: base.BaseAuthFlow):
    """
    Requests authentication from the
    user. This requires interaction
    with a web browser.
    """

    result     = urlparse.urlparse(auth_flow.credentials.redirect_url)
    host, port = get_host_info(result)

    # If we anticipate an HTTP server
    # on the local machine, create that
    # server.
    if host in LOCAL_HOST_NAMES and result.scheme == "http":
        port = port or 8080
        return local_host_response(auth_flow, port)
