from db.clients import AddClietn, UpdateClientAmount, GetClientById
from db.pay_history import AddBill, UpdateBillStatus, GetClietnHistory
from db.hosts import GetHostById, GetAllHosts
from db.codes import GetCode, ActivateCode
from db.peers import AddPeer, RemovePeer, GetPeerByClientId, GetPeerById
from db.exeption import ClientAlreadyExist, ClientNotExist, HostOrUserNotExist, PeerAlreadyExist
import pytest

# AddClietn -----------------
def test_empty_name():
    with pytest.raises(ValueError, match='Empty name'):
        AddClietn().execute(client_id=123, name='')

def test_add_client_ok():
    AddClietn().execute(client_id=123, name='123')
    client = GetClientById().execute(client_id=123)
    assert client[0] == 123

def test_client_already_exist():
    with pytest.raises(ClientAlreadyExist):
        AddClietn().execute(client_id=123, name='123')

# UpdateClientAmount -------
def test_amount_below_zero():
    with pytest.raises(ValueError, match='Amount can not be below zero'):
        UpdateClientAmount().execute(client_id=123, amount=-10)

def test_update_not_exist_client():
    UpdateClientAmount().execute(client_id=1, amount=10)

def test_update_amount_ok():
    UpdateClientAmount().execute(client_id=123, amount=10)
    client = GetClientById().execute(client_id=123)
    assert client[2] == 10


# GetClientById -------------
def test_get_not_exist_client():
    client = GetClientById().execute(client_id=1)
    assert client == None

def test_get_client_ok():
    client = GetClientById().execute(client_id=123)
    assert client[0] == 123


# AddBill -------------------
def test_amount_below_zero():
    with pytest.raises(ValueError, match='Amount below zero'):
        AddBill().execute(client_id=123, amount=-1)

def test_client_not_exist():
    with pytest.raises(ClientNotExist):
        AddBill().execute(client_id=100, amount=1)

def test_add_bill_ok():
    AddBill().execute(client_id=123, amount=10)
    bills = GetClietnHistory().execute(client_id=123)
    assert len(bills) != 0

# UpdateBillStatus ----------
def test_update_bill_amount_below_zero():
    with pytest.raises(ValueError, match='Invalid status'):
        UpdateBillStatus().execute(bill_id=123, status=-1)

def test_bill_not_exist():
    UpdateBillStatus().execute(bill_id=-1, status=1)

def test_update_bill_ok():
    bill_id = AddBill().execute(client_id=123, amount=15)
    UpdateBillStatus().execute(bill_id=bill_id, status=1)
    bills = GetClietnHistory().execute(client_id=123)
    for bill in bills:
        if bill[0] == bill_id:
            assert bill['status'] == 1

# GetClietnHistory ----------
def test_get_history_client_not_exist():
    bills = GetClietnHistory().execute(client_id=1)
    assert bills == []

def test_get_bills_history_ok():
    bills = GetClietnHistory().execute(client_id=123)
    assert len(bills) != 0


# GetHostById ---------------
def test_host_not_exist():
    assert GetHostById().execute(host_id=-1) == None

def test_get_host_ok():
    host = GetHostById().execute(host_id=1)
    assert host['id'] == 1

# GetAllHosts ---------------
def test_get_all_hosts():
    GetAllHosts().execute()


# GetCode -------------------
def test_get_not_exist_code():
    code = GetCode().execute(code=2)
    assert code is None

def test_get_exist_code():
    code = GetCode().execute(code=1)
    assert code['code'] == 1

# ActivateCode --------------
def test_activete_not_exist_code():
    ActivateCode().execute(code=2)

def test_activate_code():
    ActivateCode().execute(code=1)
    code = GetCode().execute(code=1)
    assert code['activated'] is True


# AddPeer -------------------
def test_add_peer_param_error():
    with pytest.raises(ValueError, match='Params is not Valid'):
        AddPeer().execute(client_id=123, host_id=1, params=1)

def test_add_peer_client_not_exist():
    with pytest.raises(HostOrUserNotExist):
        AddPeer().execute(client_id=-1, host_id=1, params={'a': 1})

def test_add_peer_host_not_exist():
    with pytest.raises(HostOrUserNotExist):
        AddPeer().execute(client_id=123, host_id=-1, params={'a': 1})

def test_add_peer_ok():
    AddPeer().execute(client_id=123, host_id=1, params={'a': 1})

def test_add_peer_already_exist():
    with pytest.raises(PeerAlreadyExist):
        AddPeer().execute(client_id=123, host_id=1, params={'a': 1})

# RemovePeer ----------------
def test_remove_not_exist_peer():
    RemovePeer().execute(client_id=1, host_id=1)

def test_remove_peer_ok():
    RemovePeer().execute(client_id=123, host_id=1)

# GetPeerByClientId ---------
def test_get_peer_client_not_exist():
    peers = GetPeerByClientId().execute(client_id=-1)
    assert peers == []

def test_get_peer_by_client_ok():
    AddPeer().execute(client_id=123, host_id=1, params={'a': 1})
    peers = GetPeerByClientId().execute(client_id=123)
    assert len(peers) == 1

# GetPeerById ---------------
def test_get_peer_not_exist():
    peer = GetPeerById().execute(client_id=-1, host_id=-1)
    assert peer == None

def test_get_pper_by_id_ok():
    peer = GetPeerById().execute(client_id=123, host_id=1)
    assert peer['client_id'] == 123