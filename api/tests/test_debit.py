import pytest
import debit
from wireguard.api import API
from db.peers import GetPeerById, AddPeer, RemovePeer
from db.clients import UpdateClientAmount, GetClientById
import configparser
import time
import copy

config = configparser.ConfigParser()
config.read('./config.ini')
dashboard_config = config['dashboard']
BASE_URL = dashboard_config['base_url']
LOGIN_URL = dashboard_config['login_url']
LOGIN = dashboard_config['login']
PASSWORD = dashboard_config['password']

DAY_PAY = int(config['economic']['day_pay'])

CLIENT_ID = 123
HOST_ID = 1
TIME_SLEEP = 0.5

def create_peer(api: API, name: str, host_id=HOST_ID):
    print(name)
    _, peer = api.add_peer('wg0', {'username': name})
    AddPeer().execute(client_id=CLIENT_ID, host_id=host_id, params=peer)
    return peer


def peer_in_database_check(client_id: int, host_id: int):
    peer = GetPeerById().execute(client_id, host_id)
    return peer is not None

# remove_peer --------------

def test_delete_peer_ok(request):
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    peer = create_peer(api, request.node.name)
    time.sleep(TIME_SLEEP)
    debit.remove_peer(
        api,
        CLIENT_ID,
        HOST_ID,
        peer['public_key']
    )

    assert peer_in_database_check(CLIENT_ID, HOST_ID) is False
    peer_on_host = api.get_peer_data('wg0', peer['public_key'])
    assert peer_on_host is False
    RemovePeer().execute(client_id=CLIENT_ID, host_id=HOST_ID)


def test_delete_peer_invalid_client_id(request):
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    peer = create_peer(api, request.node.name)
    time.sleep(TIME_SLEEP)
    debit.remove_peer(
        api,
        CLIENT_ID + 1,
        HOST_ID,
        peer['public_key']
    )

    assert peer_in_database_check(CLIENT_ID, HOST_ID) is True
    assert peer_in_database_check(CLIENT_ID+1, HOST_ID) is False
    peer_on_host = api.get_peer_data('wg0', peer['public_key'])
    assert peer_on_host is False
    RemovePeer().execute(client_id=CLIENT_ID, host_id=HOST_ID)


def test_delete_peer_invalid_host_id(request):
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    peer = create_peer(api, request.node.name)
    time.sleep(TIME_SLEEP)
    debit.remove_peer(
        api,
        CLIENT_ID,
        HOST_ID + 1,
        peer['public_key']
    )

    assert peer_in_database_check(CLIENT_ID, HOST_ID) is True
    assert peer_in_database_check(CLIENT_ID, HOST_ID+1) is False
    peer_on_host = api.get_peer_data('wg0', peer['public_key'])
    assert peer_on_host is False
    RemovePeer().execute(client_id=CLIENT_ID, host_id=HOST_ID)


def test_delete_peer_invalid_pubkey(request):
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    peer = create_peer(api, request.node.name)
    time.sleep(TIME_SLEEP)
    new_pubkey = copy.deepcopy(peer['public_key'])
    new_pubkey += '0'
    with pytest.raises(InterruptedError, match="Can't remove"):
        debit.remove_peer(
            api,
            CLIENT_ID,
            HOST_ID,
            new_pubkey
        )

    assert peer_in_database_check(CLIENT_ID, HOST_ID) is True
    peer_on_host = api.get_peer_data('wg0', peer['public_key'])
    assert peer_on_host is not False

    peer_on_host = api.get_peer_data('wg0', new_pubkey)
    assert peer_on_host is False
    RemovePeer().execute(client_id=CLIENT_ID, host_id=HOST_ID)
    api.remove_peer('wg0', peer['public_key'])

# debit --------------------

def test_3_peer_before_0_after(request):
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    peers = []
    for i in range(1, 4):
        peers.append(create_peer(api, f'{request.node.name}_{i}', host_id=i))
    UpdateClientAmount().execute(CLIENT_ID, DAY_PAY * 0.5)

    apis = [api, api, api]
    time.sleep(TIME_SLEEP)
    debit.debit(apis)

    for i in range(1, 4):
        assert peer_in_database_check(CLIENT_ID, i) is False
        peer_on_host = api.get_peer_data('wg0', peers[i-1]['public_key'])
        assert peer_on_host is False
        client = GetClientById().execute(client_id=CLIENT_ID)
        assert client['amount'] == 0


def test_3_peer_before_1_after(request):
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    peers = []
    for i in range(1, 4):
        peers.append(create_peer(api, f'{request.node.name}___{i}', host_id=i))
    UpdateClientAmount().execute(CLIENT_ID, DAY_PAY * 1.2)

    apis = [api, api, api]
    time.sleep(TIME_SLEEP)
    debit.debit(apis)

    for i in range(1, 4):
        peer_exist = True if i == 1 else False
        assert peer_in_database_check(CLIENT_ID, i) is peer_exist
        peer_on_host = api.get_peer_data('wg0', peers[i-1]['public_key'])
        if peer_exist:
            assert peer_on_host is not False
            debit.remove_peer(api, CLIENT_ID, i, peers[i-1]['public_key'])
        else:
            assert peer_on_host is False
        client = GetClientById().execute(client_id=CLIENT_ID)
        assert client['amount'] == 0


def test_3_peer_before_2_after(request):
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    peers = []
    for i in range(1, 4):
        peers.append(create_peer(api, f'{request.node.name}_{i}', host_id=i))
    UpdateClientAmount().execute(CLIENT_ID, DAY_PAY * 2.5)

    apis = [api, api, api]
    time.sleep(TIME_SLEEP)
    debit.debit(apis)

    for i in range(1, 4):
        peer_exist = True if i <= 2 else False
        assert peer_in_database_check(CLIENT_ID, i) is peer_exist
        peer_on_host = api.get_peer_data('wg0', peers[i-1]['public_key'])
        if peer_exist:
            assert peer_on_host is not False
            debit.remove_peer(api, CLIENT_ID, i, peers[i-1]['public_key'])
        else:
            assert peer_on_host is False
        client = GetClientById().execute(client_id=CLIENT_ID)
        assert client['amount'] == 0


def test_3_peer_before_3_after(request):
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    peers = []
    for i in range(1, 4):
        peers.append(create_peer(api, f'{request.node.name}_{i}', host_id=i))
    UpdateClientAmount().execute(CLIENT_ID, DAY_PAY * 3.5)

    apis = [api, api, api]
    time.sleep(TIME_SLEEP)
    debit.debit(apis)

    for i in range(1, 4):
        assert peer_in_database_check(CLIENT_ID, i) is True
        peer_on_host = api.get_peer_data('wg0', peers[i-1]['public_key'])
        assert peer_on_host is not False
        debit.remove_peer(api, CLIENT_ID, i, peers[i-1]['public_key'])
        client = GetClientById().execute(client_id=CLIENT_ID)
        assert client['amount'] == DAY_PAY * 0.5