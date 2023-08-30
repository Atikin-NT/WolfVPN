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

def test_show_country_list():
    url = URL + '/api/v1.0/region_list'
    r = requests.get(url)
    r = r.json()
    assert r['status'] == True
    assert type(r['data']) == list