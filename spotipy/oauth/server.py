import http
import http.server as server
import pathlib
import typing


# Templates used for generating responses
# from the local server are stored in this
# path.
TEMPLATE_ROOT = pathlib.Path(__file__).parent / "templates"

# Identify the appropriate usecase for
# each template.
TEMPLATES = {
    "success": (TEMPLATE_ROOT / "success.html"),
    "failure": (TEMPLATE_ROOT / "failure.html")
}

BASIC_REPONSE_HEADERS = {
    "Content-Type": "text-html"
}

# Used to encode incoming template
# data.
BASIC_RESPONSE_ENCODING = "utf-8"


class SpotifyHTTPServer(server.HTTPServer):
    auth_code:       typing.Optional[int]
    auth_token_form: typing.Optional[str | bytes]
    error:           typing.Optional[str]


class SpotifyRequestHandler(server.BaseHTTPRequestHandler):
    server: SpotifyHTTPServer

    def do_GET(self):
        server = self.server

        server.auth_code, server.error = None, None

        self.send_response(200)
        self.send_header(BASIC_REPONSE_HEADERS)
        self.end_headers()

        if not any([server.auth_code, server.error]):
            data = TEMPLATES["failure"].read_bytes()
        else:
            status = "successful"
            if server.error:
                status = f"failed ({server.error})"
            data = TEMPLATES["success"].read_text().format(status=status)

        write_response_html(self, data)


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

    return app
