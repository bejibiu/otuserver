import requests


def test_success_response():
    res = requests.get("http://127.0.0.1:8000")
    assert res.status_code == 200
    assert '.gitignore' in res.text


def test_bad_response():
    res = requests.get("http://127.0.0.1:8000/not_exist_folder/")
    assert res.status_code == 404
