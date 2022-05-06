"""
auth/servers.py

Used for creating local server instance.
"""


import http, pathlib, typing
import http.server as server
import urllib.parse as parse

from spotipy import errors


# Templates used for generating responses
# from the local server are stored in this
# path.
TEMPLATE_ROOT = pathlib.Path(__file__).parents[1] / "templates"

# Identify the appropriate usecase for
# each template.
TEMPLATES = {
    "success": (TEMPLATE_ROOT / "success.html"),
    "failure": (TEMPLATE_ROOT / "failure.html")
}

BASIC_REPONSE_HEADERS = (
    ("Content-Type", "text-html"),
)

# Used to encode incoming template
# data.
BASIC_RESPONSE_ENCODING = "utf-8"


class SpotifyHTTPServer(server.HTTPServer):
    auth_code:       typing.Optional[int]
    auth_token_form: typing.Optional[str | bytes]
    error:           typing.Optional[errors.SpotifyHttpError]
    state:           typing.Optional[str]


class SpotifyRequestHandler(server.BaseHTTPRequestHandler):
    server: SpotifyHTTPServer

    def do_GET(self):
        serv = self.server

        parse_url_response(self)
        self.send_response(200)
        for keyword, value in BASIC_REPONSE_HEADERS:
            self.send_header(keyword, value)
        self.end_headers()

        if not any([serv.auth_code, serv.error]):
            data = TEMPLATES["failure"].read_bytes()
        else:
            status = "successful"
            if serv.error:
                status = f"failed ({serv.error})"
            data = TEMPLATES["success"].read_text().format(status=status)

        write_response_html(self, data)


# Here lies the fields expected
# of the inbound authorization
# form.
EXPECTED_FORM_FIELDS = (
    "state",
    "code"
)


def parse_url_response(handler: SpotifyRequestHandler):
    """
    Parse the target values in
    the response form.
    """

    result = parse.urlparse(handler.path)
    form   = dict(parse.parse_qsl(result.query))

    if "error" in form:
        status = http.HTTPStatus(500)
        handler.server.error = errors.SpotifyOAuthError("",
            reason=status.description,
            code=status.value,
            http_status=status.phrase)
        return

    state, code = [form.get(f) for f in EXPECTED_FORM_FIELDS]

    handler.server.auth_code = int(code or 0)
    handler.server.state     = state


def write_response_html(handler: SpotifyRequestHandler, data: str | bytes):
    """
    Write to the target `RequestHandler`'s
    stream.
    """

    if isinstance(data, str):
        data = data.encode(BASIC_RESPONSE_ENCODING)
    handler.wfile.write(data)


def make_server(port: int, *,
    handler_cls: type[SpotifyRequestHandler] = None,
    server_cls: type[SpotifyHTTPServer] = None):
    """
    Creates a local HTTP server.
    """

    if not handler_cls:
        handler_cls = SpotifyRequestHandler
    if not server_cls:
        server_cls = SpotifyHTTPServer

    app = server_cls(("127.0.0.1", port), handler_cls)
    app.allow_reuse_address = True

    app.auth_code       = None
    app.auth_token_form = None
    app.error           = None
    app.state           = None

    return app
