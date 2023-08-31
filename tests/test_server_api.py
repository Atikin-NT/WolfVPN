import requests

URL = 'http://localhost:5001'

# check_user_login ---------
def test_chek_user_login_exist():
    url = URL + '/api/v1.0/check_user/123'
    r = requests.get(url)
    r = r.json()
    assert r['data']['user_exist'] == True

def test_chek_user_login_not_exist():
    url = URL + '/api/v1.0/check_user/10000000'
    r = requests.get(url)
    r = r.json()
    assert r['status'] == True
    assert r['data']['user_exist'] == False


# country_list -------------
def test_show_country_list():
    url = URL + '/api/v1.0/region_list'
    r = requests.get(url)
    r = r.json()
    assert r['status'] == True
    assert type(r['data']) is list


# get_client_info ----------
def test_get_client_info():
    url = URL + '/api/v1.0/user/123'
    r = requests.get(url)
    r = r.json()
    assert r['status'] == True
    assert type(r['data']['amount']) is int
    assert type(r['data']['peers']) is list

def test_get_client_info_user_not_exist():
    url = URL + '/api/v1.0/user/10000000'
    r = requests.get(url)
    r = r.json()
    assert r['status'] == False
    assert r['data'] == 'User not found'


# get_bill_history ---------
def test_get_bill_history():
    url = URL + '/api/v1.0/bill_history/123'
    r = requests.post(url)
    r = r.json()
    assert r['status'] == True
    assert type(r['data']['bills']) is list

def test_get_bill_history_user_not_exist():
    url = URL + '/api/v1.0/bill_history/10000000'
    r = requests.post(url)
    r = r.json()
    assert r['status'] == True
    assert r['data']['bills'] == []