from db.clients import AddClietn, UpdateClirentAmount, GetClientById, ClientAlreadyExist
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