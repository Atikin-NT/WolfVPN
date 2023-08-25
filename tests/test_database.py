from db.clients import AddClietn, UpdateClientAmount, GetClientById, ClientAlreadyExist
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
    print(client)

def test_get_client_ok():
    client = GetClientById().execute(client_id=123)
    assert client[0] == 123