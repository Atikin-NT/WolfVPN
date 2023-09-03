from mock import MagicMock
from wireguard.api import API
from nacl.public import PrivateKey
from base64 import b64encode
import configparser
import pytest

config = configparser.ConfigParser()
config.read('./config.ini')
dashboard_config = config['dashboard']
BASE_URL = dashboard_config['base_url']
LOGIN_URL = dashboard_config['login_url']
LOGIN = dashboard_config['login']
PASSWORD = dashboard_config['password']

# __init__ -----------------
def test_invalid_login_url():
    api = API(PASSWORD, LOGIN, "login_url", BASE_URL)
    r = api.get_config('wg0')
    assert r == False

# add_peer -----------------

def test_add_peer_invalid_data_1():
    with pytest.raises(ValueError, match='invalid data'):
        api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
        api.add_peer('wg0', {})

def test_add_peer_invalid_data_2():
    with pytest.raises(ValueError, match='invalid data'):
        api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
        api.add_peer('wg0', {'username': 123})

def test_add_peer_invalid_data_3():
    with pytest.raises(ValueError, match='invalid data'):
        api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
        api.add_peer('wg0', {'username': "   "})

def test_add_peer_no_allowed_ips():
    with pytest.raises(ValueError, match='no allowed ips'):
        api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
        api._available_ips = MagicMock()
        api._available_ips.return_value = ''
        api.add_peer('wg0', {'username': "name"})

def test_add_peer_ok():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    r, _ = api.add_peer('wg0', {'username': "name"})
    assert r ==  True

# remove_peer --------------

def test_delete_exist_peer():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    r, peer = api.add_peer('wg0', {'username': "name"})
    r = api.remove_peer('wg0', [peer['public_key']])
    assert r == True

def test_delete_non_exist_peer():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    key = PrivateKey.generate()
    r = api.remove_peer('wg0', [b64encode(bytes(key.public_key)).decode('ascii')])
    assert r == False

# get_config ---------------

def test_get_invalid_config():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    r = api.get_config('wg1')
    assert r == False

def test_get_valid_config():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    r = api.get_config('wg0')
    assert r['checked'] == 'checked'

# get_peer_data ------------

def test_get_exist_data():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    r, peer = api.add_peer('wg0', {'username': 'get_exist_peer_data'})
    assert r == True

    r = api.get_peer_data('wg0', peer['public_key'])
    assert r['private_key'] == peer['private_key']

def test_get_not_exist_data():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    key = PrivateKey.generate()
    r = api.get_peer_data('wg0', b64encode(bytes(key.public_key)).decode('ascii'))
    assert r == False

# qrcode -------------------
def test_qrcode_exist():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    r, peer = api.add_peer('wg0', {'username': 'test_qrcode_exist'})
    assert r == True

    r = api.qrcode('wg0', peer['public_key'])
    assert 'data:image/png' in r

def test_qrcode_not_exist():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    key = PrivateKey.generate()
    r = api.qrcode('wg0', b64encode(bytes(key.public_key)).decode('ascii'))
    assert r == False

# download -----------------
def test_download_ok():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    r, peer = api.add_peer('wg0', {'username': 'test_download_ok'})
    assert r == True

    r = api.download('wg0', peer['public_key'])
    assert r['status'] == True
    assert '[Interface]' in r['content']

def test_download_peer_not_exist():
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    key = PrivateKey.generate()
    r = api.download('wg0', b64encode(bytes(key.public_key)).decode('ascii'))
    assert r['status'] == False
