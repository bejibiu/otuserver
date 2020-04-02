import os

from pytest import fixture

from httpd import Server


@fixture
def server():
    return Server()


def test_method_list_dir(server):
    res = server.method_get('\\')
    assert '\r\n'.join(os.listdir(server.DOCUMENT_ROOT)) in res
