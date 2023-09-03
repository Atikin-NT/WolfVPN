from nacl.public import PrivateKey
from base64 import b64encode

def check_param_peer_data(data: dict):
    if 'username' in data and type(data['username']) is str and data['username'].strip() != '':
        return True
    return False

def create_data_for_add_peer():
    key = PrivateKey.generate()
    params = {
        "private_key": b64encode(bytes(key._private_key)).decode('ascii'),
        "public_key": b64encode(bytes(key.public_key)).decode('ascii'),
        "allowed_ips": None,
        "name": None,
        "DNS": "1.1.1.1",
        "endpoint_allowed_ip": "0.0.0.0/0",
        "MTU": "1420",
        "keep_alive": "21",
        "enable_preshared_key": False,
        "preshared_key": ""
    }
    return params