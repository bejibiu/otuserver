import socket
import os
from _asyncio import get_event_loop

from pytest import fixture

from httpd import Server, HandleClient


@fixture
def server():
    return Server()


@fixture
def handle():
    loop = get_event_loop()
    client_socket = socket.socket()
    return HandleClient(loop, client_socket)


def test_method_list_dir(handle):
    handle.method_get('\\')
    assert '''<html>
    <head>
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
    </body>
</html>
''' in handle.body


def test_file_with_query_string(handle):
    handle.method_get('/httptest/dir2/page.html/')
    assert "HTTP/1.1 404 Not Found" in handle.buffer_response


def test_file_type_jpg(handle):
    handle.method_get('/httptest/160313.jpg')
    assert "Content-Type:image/jpeg" in handle.buffer_response


def test_file_type_plant_file_without_ext(handle):
    handle.method_get('/httptest/new')
    assert "Content-Type:plan/text" in handle.buffer_response


def test_file_without_(handle):
    handle.method_get('/httptest/../../../../../../../new')
    assert "HTTP/1.1 404 Not Found" in handle.buffer_response

