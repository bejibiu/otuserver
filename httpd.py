import asyncio
import argparse
import mimetypes
import os
import socket
import logging
import urllib
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DEFAULT_ERROR_MESSAGE = """\
<html>
    <head>
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
    </body>
</html>
"""


class Server:

    def __init__(self, bind_ip="127.0.0.1", bind_port=8000, backlog=5, document_root=None, loop=None):
        self.loop = loop
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.backlog = backlog
        self.server = None
        self.document_root = document_root

    def create_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.bind_ip, self.bind_port))
        logging.info(f"server bind on {self.bind_ip}:{self.bind_port}. http://{self.bind_ip}:{self.bind_port}")
        self.server.listen(self.backlog)
        self.server.setblocking(False)

    async def run_forever(self):
        while True:
            client_sock, address = await self.loop.sock_accept(self.server)
            logging.info(f'accept from {address}')
            handle_client = HandleClient(loop, client_sock, self.document_root)
            self.loop.create_task(handle_client.handle_client())


class HandleClient:
    OK = 200
    BAD_REQUEST = 400
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_ERROR = 500
    STATUS = {
        OK: "OK",
        BAD_REQUEST: "Bad Request",
        FORBIDDEN: "Forbidden",
        NOT_FOUND: "Not Found",
        METHOD_NOT_ALLOWED: "Method Not Allowed",
        INTERNAL_ERROR: "Internal Server Error",
    }
    version_protocol = 'HTTP/1.1'

    def __init__(self, loop, client_socket, document_root=BASE_DIR):
        self.DOCUMENT_ROOT = document_root
        self.loop = loop
        self.client_socket = client_socket
        self.body = ""
        self.method = None
        self.buffer_response = []
        self.loop = loop
        self.file_size = 0

    async def handle_client(self):

        handler_method = {
            "GET": self.method_get,
            "HEAD": self.method_get
        }
        request = await self.recv_from_socket()
        logging.info(f'recv: {request}')
        request_head = request.split("\r\n")[0]
        self.method, uri, _ = request_head.split()

        handler = handler_method.get(self.method, self.method_not_allow)
        try:
            handler(uri)
        except Exception as e:
            logging.exception(e)
            self.buffer_response = []
            self.add_headers_response(500)
            self.body = ""
        logging.info(f'response: {self.body}')

        await self.send_response(self.client_socket)
        self.client_socket.close()

    async def recv_from_socket(self):
        buffer_message = ""

        while True:
            message = (await self.loop.sock_recv(self.client_socket, 1024)).decode()
            if "\r\n" in message or len(message) == 0:
                return buffer_message + message
            buffer_message += message
            logging.error(f"len={message}, buf={buffer_message}")

    async def send_response(self, sock):
        response = "\r\n".join(self.buffer_response)
        response = bytes(response.encode())
        response += b"\r\n\r\n"
        if self.method != "HEAD":
            response += self.body if isinstance(self.body, bytes) else self.body.encode()
        await self.loop.sock_sendall(sock, data=response)

    def get_path(self, uri: str):
        norm_uri = urllib.parse.unquote(uri)
        norm_uri = norm_uri.partition("?")[0]
        norm_uri = os.path.abspath(norm_uri)
        norm_uri = norm_uri.lstrip("/")
        path = os.path.join(self.DOCUMENT_ROOT, norm_uri)
        if uri.endswith("/"):
            path += "/"
        return path

    def method_get(self, uri):
        path = self.get_path(uri)
        if not os.path.exists(path):
            return self.add_headers_response(self.NOT_FOUND)
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        self.method_load_index(path)

    def method_load_index(self, path):
        logging.info(path)
        try:
            self.file_size = os.path.getsize(path)
            with open(path, 'rb') as file:
                if self.method == "GET":
                    self.body = file.read()
        except FileNotFoundError:
            self.add_headers_response(404)
            self.body = DEFAULT_ERROR_MESSAGE
            self.add_headers('Content-Type', mimetypes.types_map[".html"])
        except PermissionError:
            self.add_headers_response(403)
            self.body = DEFAULT_ERROR_MESSAGE
            self.add_headers('Content-Type', mimetypes.types_map[".html"])
        else:
            self.add_headers_response(200)
            file_ext = os.path.splitext(path)[-1]
            self.add_headers('Content-Type', mimetypes.types_map.get(file_ext, 'application/octet-stream'))
        self.add_headers('Date', datetime.now())
        self.add_headers('Server', "Otuserver")
        self.add_headers('Connection', 'close')
        self.add_headers('Content-Length', self.file_size or len(self.body))

    def method_not_allow(self, *args):
        return self.add_headers_response(self.METHOD_NOT_ALLOWED)

    def add_headers_response(self, status_code):
        self.buffer_response.append(f"{self.version_protocol} {status_code} {self.STATUS[status_code]}")

    def add_headers(self, name, value):
        self.buffer_response.append(f"{name}: {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default="127.0.0.1", help="address to interface for server")
    parser.add_argument('--port', default=8000, type=int, help="port to listen ")
    parser.add_argument('--file-log', default=None, help='path to log file')
    parser.add_argument('--backlog', default=100, type=int, help='backlog')
    parser.add_argument('-r', '--document-root', default=BASE_DIR, help='root folder for server')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s',
                        filename=args.file_log,
                        datefmt='%Y.%m.%d %H:%M:%S')
    loop = asyncio.get_event_loop()
    server = Server(args.host, args.port, args.backlog, args.document_root, loop)
    server.create_server()
    loop.run_until_complete(server.run_forever())
