import requests
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')
KEY = config['api_key']['key']
URL = config['url']['api_url']


def get_all_clients_list():
    r = requests.post(URL + '/api/v1.0/get_all_clients', json={'key': KEY})
    data = r.json()
    return data['data']['clients']

def remove_peer(client_id: int, host_id: int):
    r = requests.post(
        URL + '/api/v1.0/remove_peer', 
        json={
            'client_id': client_id,
            'host_id': host_id
        })
    if r.status_code != 200:
        return False
    data = r.json()
    return data['status']


def update_client_amount(client_id: int, amount: int):
    r = requests.post(
        URL + '/api/v1.0/update_client_amount', 
        json={
            'client_id': client_id,
            'amount': amount,
            'key': KEY
        })
    if r.status_code != 200:
        return False
    data = r.json()
    return data['status']

if __name__ == '__main__':
    get_all_clients_list()
