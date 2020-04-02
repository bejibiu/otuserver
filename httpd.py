import asyncio
import argparse
import os
import socket
import logging

BASE_DIR = os.path.dirname(__file__)

from http import server


class Server:
    DOCUMENT_ROOT = BASE_DIR
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

    def __init__(self, bind_ip="127.0.0.1", bind_port=8000, backlog=5, loop=None):
        self.body = None
        self.method = None
        self.buffer_request = []
        self.loop = loop
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.backlog = backlog
        self.server = None

    def create_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.bind_ip, self.bind_port))
        logging.info(f"server bind on {self.bind_ip}:{self.bind_port}. http://{self.bind_ip}:{self.bind_port}")
        self.server.listen(self.backlog)
        self.server.setblocking(False)

    async def run_forever(self):
        while True:
            client_sock, address = await self.loop.sock_accept(self.server)
            logging.info(f'accept from {address}')
            self.loop.create_task(self.handle_client(client_sock))

    async def handle_client(self, sock: socket):

        handler_method = {
            "GET": self.method_get,
            "HEAD": self.method_get
        }
        request = (await self.loop.sock_recv(sock, 1024)).decode()
        logging.info(f'recv: {request}')
        request_head = request.split("\r\n")[0]
        self.method, uri, _ = request_head.split()

        handler = handler_method.get(self.method, self.method_not_allow)
        handler(uri)
        logging.info(f'response: {self.body}')

        await self.send_response(sock)
        sock.close()

    async def send_response(self, sock):
        response = "\r\n".join(self.buffer_request)
        if self.method != "HEAD":
            response += f"\r\n\r\n{self.body}"

        await self.loop.sock_sendall(sock, data=response.encode())

    @staticmethod
    def make_safe_uri(uri):
        uri = f".{os.path.sep}{uri}"
        uri = os.path.normpath(uri)
        return uri

    def method_get(self, uri):
        safe_uri = self.make_safe_uri(uri)
        path = os.path.join(self.DOCUMENT_ROOT, safe_uri)
        if not os.path.exists(path):
            return self.add_headers_response(self.NOT_FOUND)
        if os.path.isdir(path):
            return self.method_list_dir(path)
        with open(path, 'rb') as f:
            self.body = f.read()
        self.add_headers_response(200)

    def method_list_dir(self, path):
        self.body = '\r\n'.join(os.listdir(path))
        self.add_headers_response(200)

    def method_not_allow(self, *args):
        return self.add_headers_response(self.METHOD_NOT_ALLOWED)

    def add_headers_response(self, status_code):
        self.buffer_request.append(f"{self.version_protocol} {status_code} {self.STATUS[status_code]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default="127.0.0.1", help="address to interface for server")
    parser.add_argument('--port', default=8000, type=int, help="port to listen ")
    parser.add_argument('--file-log', default=None, help='path to log file')
    parser.add_argument('--backlog', default=5, type=int, help='backlog')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s',
                        filename=args.file_log,
                        datefmt='%Y.%m.%d %H:%M:%S')
    loop = asyncio.get_event_loop()
    server = Server(args.host, args.port, args.backlog, loop=loop)
    server.create_server()
    loop.run_until_complete(server.run_forever())
