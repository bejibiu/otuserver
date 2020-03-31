import asyncio
import os
import socket
import logging

bind_ip = "127.0.0.1"
bind_port = 8000
backlog = 5
BASE_DIR = os.path.dirname(__file__)
DOCUMENT_ROOT = BASE_DIR


def create_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    logging.info(f"server bind on {bind_ip}:{bind_port}. http://{bind_ip}:{bind_port}")
    server.listen(backlog)
    server.setblocking(False)
    return server


async def handle_client(sock: socket, loop):
    handler_method = {
        "GET": method_get,
        "HEAD": method_head
    }
    request = (await loop.sock_recv(sock, 1024)).decode()
    logging.info(f'recv: {request}')
    request_head = request.split("\r\n")[0]
    method, uri, _ = request_head.split()
    handler = handler_method.get(method, method_not_allow)
    response = handler(uri)
    logging.info(f'response: {response}')
    await loop.sock_sendall(sock, data=response.encode())
    sock.close()


def make_safe_uri(uri):
    uri = f".{os.path.sep}{uri}"
    uri = os.path.normpath(uri)
    return uri


def method_get(uri):
    safe_uri = make_safe_uri(uri)
    path = os.path.join(DOCUMENT_ROOT, safe_uri)
    if not os.path.exists(path):
        return "HTTP/1.1 404 NOT FOUND"
    if os.path.isdir(path):
        return method_list_dir(path)
    with open(path, 'rb') as f:
        data = f.read()
    return f"HTTP/1.1 200 OK\r\n\r\n{data}"


def method_list_dir(path):
    list_dir = '\r\n'.join(os.listdir(path))
    return f"HTTP/1.1 200 OK\r\n\r\n{list_dir}"


def method_head(uri):
    return method_not_allow()


def method_not_allow(*args):
    return "HTTP/1.1 405 Method Not Allowed"


async def run_forever(server: socket, loop):
    while True:
        client_sock, address = await loop.sock_accept(server)
        logging.info(f'accept from {address}')
        loop.create_task(handle_client(client_sock, loop))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s',
                        filename=None,
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = create_server()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_forever(server, loop))
