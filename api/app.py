from flask import Flask, jsonify, request
from flask_cors import CORS
from db.clients import GetClientById, AddClient
from db.hosts import GetAllHosts
from db.peers import GetPeerByClientId, GetPeerById, AddPeer, RemovePeer
from db.pay_history import GetClietnHistory
from db.exeption import *
from bot import send_file_to_user
from wireguard.api import API
from aiogram.types.input_file import BufferedInputFile
import utils
import asyncio
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')
dashboard_config = config['dashboard']

all_confs = utils.create_ini_config_list(dict(dashboard_config))
apis = []
for conf in all_confs:
    apis.append(API(
        conf['password'],
        conf['login'],
        conf['login_url'],
        conf['base_url']
    ))

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


@app.route('/api/v1.0/add_peer', methods=['POST'])
def add_peer():
    """добавить новое подключение

    Args:
        client_id (int): id пользователя из телеги
        host_id (int): id хоста
        username (str): ник пользователя
    """
    answer = json_template.copy()
    request_data = request.get_json()
    if 'username' not in request_data or 'client_id' not in request_data or 'host_id' not in request_data:
        answer['status'] = False
        answer['data'] = 'Not all values was presented'
        return jsonify(answer)
    client_id = request_data['client_id']
    host_id = int(request_data['host_id'])

    try:
        data, params = apis[host_id-1].add_peer('wg0', request_data)
        AddPeer().execute(client_id, host_id, params)
    except Exception as msg:
        answer['status'] = False
        answer['data'] = str(msg)
        return jsonify(answer)
    answer['data'] = 'ok'
    return jsonify(answer)


@app.route('/api/v1.0/remove_peer', methods=['POST'])
def remove_peer():
    """добавить новое подключение

    Args:
        client_id (int): id пользователя из телеги
        host_id (int): id хоста
    """
    answer = json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'host_id' not in request_data:
        answer['status'] = False
        answer['data'] = 'Not all values was presented'
        return jsonify(answer)
    client_id = request_data['client_id']
    host_id = int(request_data['host_id'])

    try:
        peer = GetPeerById().execute(client_id, host_id)
        if peer is None:
            raise InterruptedError("peer not exist")
        res = apis[host_id-1].remove_peer('wg0', [peer['params']['public_key']])
        if res is False:
            raise InterruptedError("Can't remove")
        RemovePeer().execute(client_id, host_id)
    except Exception as msg:
        answer['status'] = False
        answer['data'] = str(msg)
        return jsonify(answer)
    answer['data'] = 'ok'
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
    """
    answer = json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'host_id' not in request_data:
        answer['status'] = False
        answer['data'] = 'Client id and host id not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    host_id = int(request_data['host_id'])

    try:
        peer = GetPeerById().execute(client_id, host_id)
        if peer is None:
            answer['status'] = False
            answer['data'] = 'Peer not found'
            return jsonify(answer)

        qrcode_str = apis[host_id-1].qrcode('wg0', peer['params']['public_key'])
        answer['data'] = {'qrcode': qrcode_str}
    except Exception as msg:
        answer['status'] = False
        answer['data'] = str(msg)

    return jsonify(answer)


@app.route('/api/v1.0/download', methods=['POST'])
def download():
    """скачивание файла для подключения

    Args(POST):
        client_id (int): id пользователя из телеги
        host_id (int): id сервера из БД
    """
    answer = json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'host_id' not in request_data:
        answer['status'] = False
        answer['data'] = 'Client id and host id not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    host_id = int(request_data['host_id'])

    peer = GetPeerById().execute(client_id, host_id)
    if peer is None:
        answer['status'] = False
        answer['data'] = 'Peer not found'
        return jsonify(answer)

    try:
        file = apis[host_id-1].download('wg0', peer['params']['public_key'])
        if file is False:
            raise InterruptedError('can`t get file')
        print(file)
        file_content, file_title = file['content'], file['filename']
        file = bytes(file_content, 'utf-8')
        input_file = BufferedInputFile(file=file, filename=file_title)

        asyncio.run(send_file_to_user(client_id, input_file))
    except Exception as msg:
        answer['status'] = False
        answer['data'] = str(msg)
        return jsonify(answer)

    answer['data'] = 'ok'
    return jsonify(answer)


if __name__ == '__main__':
    app.run(port=5001)
