"""
Tools for generating simple web servers. These
web servers are intended to be used as a proxy
the remote `OAuth2.0` server can probe for user
approval.
"""

# --------------------------------------------- #
# Local Host/Server Objects. In some cases of
# obtaining authentication from a user, there
# needs to be a redirect to another host/server.
# The below defines a procedure for generating a
# temporary local server available for this
# purpose.
# --------------------------------------------- #

import pathlib, http, http.server, urllib.parse, webbrowser

from ampyr import errors, typedefs as td
from ampyr.oauth2 import base

LOCALHOST_ALIASES = ("127.0.0.1", "localhost")
"""
A collection of values that identify a host as
'localhost'.
"""

SERVER_TEMPLATE_ROOT = pathlib.Path(__file__).parents[1] / "templates"
"""
Templates directory. Serves to contain HTML files
that define the template responses from this
local server.
"""

SERVER_TEMPLATES = {
    "success": (SERVER_TEMPLATE_ROOT / "oauth_success.html"),
    "failure": (SERVER_TEMPLATE_ROOT / "oauth_failure.html")}
"""
Mapping for the appropriate template according
to the response being sent.
"""

SERVER_RESPONSE_HEADERS = [("Content-Type", "text-html")]
"""Basic Response Headers configuration."""

SERVER_RESPONSE_ENCODING = "utf-8"
"""Use to encode incoming template data."""

SERVER_EXPECTED_FORMFIELDS = ("state", "code")
"""
Series of fieldnames expected to be found in
`AuthHTTPServer` response.
"""


def get_user_auth(flow: base.SimpleOAuth2Flow):
    """
    Requests authorization from the user. This
    requires interaction with a web browser.
    """

    scheme, host, port = _get_host_info(flow)

    # If we anticipate the HTTP server on the
    # local machine, create that server and open
    # a browser window pointing to it.
    if host in LOCALHOST_ALIASES and scheme == "http":
        port = port or 8080
        return _request_user_auth(flow, port)


def _get_host_info(flow: base.SimpleOAuth2Flow):
    """Returns the host and port information."""

    result = urllib.parse.urlparse(flow.auth_config.url_for_redirect)
    return result.scheme, result.netloc.split(":")[0], result.port


def _request_user_auth(flow: base.SimpleOAuth2Flow, port: int):
    """
    Attempt to get authorization from the user
    via their browser.
    """

    server = _open_auth_server(port)

    if not flow.url_for_oauth:
        raise errors.OAuthValueError(
            f"{type(flow).__name__} missing oauth URL.")

    webbrowser.open(flow.url_for_oauth)
    server.handle_request()

    if server.error:
        raise server.error

    # Ensure the state was recieved correctly.
    # State recieved should match state sent.
    if flow.auth_config.state and server.state != flow.auth_config.state:
        raise errors.OAuth2BadStateError(
            "OAuth2.0 state recieved from server "
            "does not match the state sent.",
            status=http.HTTPStatus(409))

    if server.auth_code:
        return server.auth_code

    # If failure to obtain an auth_code, throw an
    # OAuth2.0 error
    raise errors.OAuth2HttpError(
        "no authentication code was recieved.", status=http.HTTPStatus(401))


def _open_auth_server(port: int):
    """Create a local HTTP server."""

    server = LocalHTTPServer((LOCALHOST_ALIASES[0], port), LocalRequestHandler)

    server.allow_reuse_address = True

    server.auth_code       = None
    server.auth_token_form = None
    server.error           = None
    server.state           = None

    return server


class LocalHTTPServer(http.server.HTTPServer):
    """
    Derivitive of `http.server.HTTPServer`. Used
    as a proxy for requesting approval from the
    user.
    """

    auth_code: td.OptString
    """
    Code representing the state of authorization.
    """

    auth_token_form: td.Optional[td.StrOrBytes]
    """
    Form used to confirm/deny authorization from
    the user.
    """

    error: td.Optional[errors.OAuth2HttpError]
    """
    Error that occurred during user
    authorization.
    """

    state: td.OptString
    """State of authorization."""


class LocalRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Derived from
    `http.server.BaseHTTPRequestHandler`. Used to
    handle requests from/against a local
    `LocalHTTPServer` instance.
    """

    server: LocalHTTPServer
    """
    Server used to handle the user authorization
    requests.
    """

    def do_GET(self):
        _parse_server_response(self)
        self.send_response(200)

        for key, value in SERVER_RESPONSE_HEADERS:
            self.send_header(key, value)
        self.end_headers()

        status, message = "failure", "bad request."

        if self.server.error:
            message = f"failed {self.server.error!s}"
        elif self.server.auth_code:
            status, message = "success", "ok."

        _write_server_response(self, status, message)

    # Silence handler's log.
    def log_message(self, format: str, *args) -> None:
        return


def _parse_server_response(handler: LocalRequestHandler):
    """
    Parse the target values in the response form.
    """

    result = urllib.parse.urlparse(handler.path)
    form   = dict(urllib.parse.parse_qsl(result.query))

    if "error" in form:
        handler.server.error = errors.OAuth2HttpError()
        return

    state, code = [form.get(f) for f in SERVER_EXPECTED_FORMFIELDS]
    handler.server.auth_code = code
    handler.server.state     = state


def _write_server_response(
    handler: LocalRequestHandler, status: str, message: str):
    """
    Write to the target `LocalRequestHandler`'s
    stream.
    """

    data = (SERVER_TEMPLATES[status]
        .read_text()
        .format(status=status)
        .encode(SERVER_RESPONSE_ENCODING))
    handler.wfile.write(data)
