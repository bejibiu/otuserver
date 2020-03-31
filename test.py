import os
from httpd import method_get


def test_method_list_dir():
    path = "\\"
    res = method_get(path)
    assert '\r\n'.join(os.listdir(path)) in res
