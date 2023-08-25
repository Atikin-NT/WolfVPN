from db.clients import AddClietn, UpdateClientAmount, GetClientById, ClientAlreadyExist
from db.pay_history import AddBill, UpdateBillStatus, GetClietnHistory, ClientNotExist
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
    print(bills)
    assert len(bills) != 0

# UpdateBillStatus ----------
def test_update_bill_amount_below_zero():
    with pytest.raises(ValueError, match='Amount below zero'):
        UpdateBillStatus().execute(bill_id=123, amount=-1)

def test_bill_not_exist():
    UpdateBillStatus().execute(bill_id=-1, amount=1)

def test_update_bill_ok():
    bill_id = AddBill().execute(client_id=123, amount=15)
    UpdateBillStatus().execute(bill_id=bill_id, amount=1)
    bills = GetClietnHistory().execute(client_id=123)
    for bill in bills:
        if bill[0] == bill_id:
            assert bill['amount'] == 1

# GetClietnHistory ----------
def test_get_history_client_not_exist():
    bills = GetClietnHistory().execute(client_id=1)
    assert bills == []

def test_get_bills_history_ok():
    bills = GetClietnHistory().execute(client_id=123)
    assert len(bills) != 0