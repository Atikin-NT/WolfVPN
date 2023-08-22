from mock import MagicMock
from wireguard.session import Request

def test_invalid_url():
    req = Request("test", "test", "login_url")
    assert req.get("invalid url", {}) == False

def test_login_with_error():
    req = Request("pass", "usernameы", "login_url")
    req.mock_true("url", {})