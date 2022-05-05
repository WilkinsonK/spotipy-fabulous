import http
import http.server as server
import inspect
import pathlib


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


class BasicRequestHandler(server.BaseHTTPRequestHandler):

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


def write_response_html(handler: BasicRequestHandler, data: str | bytes):
    """
    Write to the target `RequestHandler`'s
    stream.
    """

    if isinstance(data, str):
        data = data.encode(BASIC_RESPONSE_ENCODING)
    handler.wfile.write(data)


HTTP_DEFAULT_HANDLER = BasicRequestHandler
HTTP_DEFAULT_SERVER  = server.HTTPServer
HTTP_LOCAL_ADDRESS   = "127.0.0.1"


def make_server(port: int, *,
    handler_cls: type[BasicRequestHandler] = None,
    server_cls: type[server.HTTPServer] = None):
    """
    Creates a local HTTP server.
    """

    if not handler_cls:
        handler_cls = HTTP_DEFAULT_HANDLER
    if not server_cls:
        server_cls = HTTP_DEFAULT_SERVER

    app = server_cls((HTTP_LOCAL_ADDRESS, port), handler_cls)
    app.allow_reuse_address = True

    app.auth_code       = None
    app.auth_token_form = None
    app.error           = None

    return server
