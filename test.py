import os
from httpd import method_get, DOCUMENT_ROOT


def test_method_list_dir():
    path = DOCUMENT_ROOT
    res = method_get('\\')
    assert '\r\n'.join(os.listdir(path)) in res
