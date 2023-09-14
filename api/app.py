from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from db.clients import GetClientById, AddClient
from db.hosts import GetAllHosts
from db.peers import GetPeerByClientId, GetPeerById
from db.pay_history import GetClietnHistory
from db.exeption import *

from wireguard.api import API
import utils

import configparser
config = configparser.ConfigParser()
config.read('./config.ini')
dashboard_config = config['dashboard']

api = API(
    dashboard_config['password'],
    dashboard_config['login'],
    dashboard_config['login_url'],
    dashboard_config['base_url']
)

DAY_PAY = int(config['economic']['day_pay'])
CONF_NAME = dashboard_config['config_name']

app = Flask(__name__)
CORS(app)

json_template = {
    'status': True,
    'data': ''
}

 
@app.route('/api/v1.0/check', methods=['GET'])
def check():
    "Проверка связи"
    return jsonify(json_template)


# start page ----------
@app.route('/api/v1.0/check_user/<int:user_id>', methods=['GET'])
def user_login_check(user_id: int):
    """Проверка на наличие пользователя в системе

    Args:
        user_id (int): id пользователя из телеги
    """
    client = GetClientById().execute(user_id)
    answer = json_template.copy()

    answer['data'] = {'user_exist': True}
    if client is None:
        answer['data']['user_exist'] = False
    
    return jsonify(answer)


@app.route('/api/v1.0/add_user/', methods=['POST'])
def add_user():
    """Добавление нового пользователя в систему

    Args:
        client_id (int): id пользователя из телеги
        name (str): имя пользователя
    """
    answer = json_template.copy()
    request_data = request.get_json()

    if 'client_id' not in request_data or 'name' not in request_data:
        answer['status'] = False
        answer['data'] = 'Client id and name not presented'
        return jsonify(answer)
    
    client_id = request_data['client_id']
    name = request_data['name']

    try:
        AddClient().execute(client_id, name);
    except ValueError:
        answer['status'] = False
        answer['data'] = 'name is empty'
    except ClientAlreadyExist:
        pass
    
    return jsonify(answer)


@app.route('/api/v1.0/region_list', methods=['GET'])
def region_list():
    "Получить список серверов"
    regions = GetAllHosts().execute()
    regions = utils.get_permited_keys_from_dict_list(regions, ['id', 'region'])
    
    answer = json_template.copy()
    answer['data'] = regions
    return jsonify(answer)


# main page -----------
@app.route('/api/v1.0/user/<int:client_id>', methods=['GET'])
def get_client(client_id: int):
    """получение информации о пользователе

    Args:
        client_id (int): id пользователя из телеги
    """
    answer = json_template.copy()

    client = GetClientById().execute(client_id)
    if client is None:
        answer['status'] = False
        answer['data'] = 'User not found'
        return jsonify(answer)

    client_peers = GetPeerByClientId().execute(client_id)
    client_peers = utils.get_permited_keys_from_dict_list(client_peers, ['client_id', 'host_id'])
    
    regions = GetAllHosts().execute()
    regions = utils.get_permited_keys_from_dict_list(regions, ['id', 'region'])

    client_peers = [peer | {'region': utils.dict_search(regions, 'id', peer['host_id'], 'region')}
                    for peer in client_peers]
    
    answer['data'] = {
        'amount': client['amount'],
        'day_left': client['amount'] // DAY_PAY,
        'peers': client_peers
    }
    return jsonify(answer)


@app.route('/api/v1.0/bill_history/<int:client_id>', methods=['POST'])
def bill_history(client_id: int):
    """получение чековой истории пользователя

    Args:
        client_id (int): id пользователя из телеги
    """
    bill_history = GetClietnHistory().execute(client_id)
    answer = json_template.copy()

    answer['data'] = {'bills': bill_history}
    return jsonify(answer)


@app.route('/api/v1.0/qrcode/', methods=['POST'])
def qrcode():
    """получение qr кода кнкретного подключения

    Args(POST):
        client_id (int): id пользователя из телеги
        host_id (int): id сервера из БД

    Returns:
        _type_: _description_
    """
    answer = json_template.copy()

    request_data = requests.get_json()

    if 'client_id' not in request_data or 'host_id' not in request_data:
        answer['status'] = False
        answer['data'] = 'Client id and host id not presented'
        return jsonify(answer)
    
    client_id = request_data['client_id']
    host_id = request_data['host_id']

    peer = GetPeerById().execute(client_id, host_id)
    if peer is None:
        answer['status'] = False
        answer['data'] = 'Peer not found'
        return jsonify(answer)

    qrcode_str = api.qrcode(CONF_NAME, peer['params']['public_key'])

    answer['data'] = {'qrcode': qrcode_str}
    return jsonify(answer)

if __name__ == '__main__':
    app.run(port=5001)