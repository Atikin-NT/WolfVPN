from flask import Blueprint, jsonify, request
from db.clients import GetClientById, AddClient, UpdateClientAmount, GetAllClients
from db.peers import GetPeerByClientId
from db.hosts import GetAllHosts
import db.exeption as ex
import utils
import configparser
import logging

config = configparser.ConfigParser()
config.read('./config.ini')
DAY_PAY = int(config['economic']['day_pay'])
KEY = config['debit']['key']

client_api = Blueprint('client_api', __name__)
logger = logging.getLogger('gunicorn.error')


@client_api.route('/api/v1.0/check_user/<int:user_id>', methods=['GET'])
def user_login_check(user_id: int):
    """Проверка на наличие пользователя в системе

    Args:
        user_id (int): id пользователя из телеги
    """
    logger.info(f'user_login_check, user_id = {user_id}')
    client = GetClientById().execute(user_id)
    answer = utils.json_template.copy()

    answer['data'] = {'user_exist': True}
    if client is None:
        answer['data']['user_exist'] = False

    return jsonify(answer)


@client_api.route('/api/v1.0/add_user/', methods=['POST'])
def add_user():
    """Добавление нового пользователя в систему

    Args:
        client_id (int): id пользователя из телеги
        name (str): имя пользователя
    """
    logger.info('add_user')
    answer = utils.json_template.copy()
    request_data = request.get_json()

    if 'client_id' not in request_data or 'name' not in request_data:
        logger.error(f'invalid params in add_user: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Client id and name not presented'
        return jsonify(answer)

    client_id = request_data['client_id']
    name = request_data['name']

    try:
        AddClient().execute(client_id, name)
        UpdateClientAmount().execute(client_id, DAY_PAY * 2)
    except (ValueError, ex.ClientAlreadyExist) as e:
        logger.error(f'add client: client_id = {client_id}, ex = {e}, name = {name}')
        answer['status'] = False
        answer['data'] = str(e)

    return jsonify(answer)

@client_api.route('/api/v1.0/user/<int:client_id>', methods=['GET'])
def get_client(client_id: int):
    """получение информации о пользователе

    Args:
        client_id (int): id пользователя из телеги
    """
    logger.info('get_client')
    answer = utils.json_template.copy()

    client = GetClientById().execute(client_id)
    if client is None:
        logger.error(f'Client not found: client_id = {client_id}')
        answer['status'] = False
        answer['data'] = 'User not found'
        return jsonify(answer)

    client_peers = GetPeerByClientId().execute(client_id)
    client_peers = utils.get_permited_keys_from_dict_list(client_peers, ['client_id', 'host_id'])

    regions = GetAllHosts().execute()
    regions = utils.get_permited_keys_from_dict_list(regions, ['id', 'region'])

    client_peers = [peer | {'region': utils.dict_search(regions, 'id', peer['host_id'], 'region')}
                    for peer in client_peers]
    
    if len(client_peers) == 0 or client['amount'] == 0:
        day_left = 'ꝏ'
    else:
        day_left = client['amount'] // (DAY_PAY * len(client_peers))

    answer['data'] = {
        'amount': client['amount'],
        'day_left': day_left,
        'peers': client_peers
    }
    return jsonify(answer)


@client_api.route('/api/v1.0/get_all_clients', methods=['POST'])
def get_all_clients():
    """полученить список всех клиентов
    """
    logger.info('get clients list')
    answer = utils.json_template.copy()

    request_data = request.get_json()
    if 'key' not in request_data or request_data['key'] != KEY:
        logger.error(f'no key in get_all_clients: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Key not presented'
        return jsonify(answer)

    clients = GetAllClients().execute()
    for client in clients:
        client['peers'] = []
        peers = GetPeerByClientId().execute(client['id'])
        for peer in peers:
            client['peers'].append({
                'host_id': peer['host_id']
            })

    answer['data'] = {'clients': clients}

    return jsonify(answer)


@client_api.route('/api/v1.0/update_client_amount', methods=['POST'])
def update_client_amount():
    """побновить баланс пользователя
    """
    logger.info('update_client_amount')
    answer = utils.json_template.copy()

    request_data = request.get_json()
    if 'client_id' not in request_data or 'amount' not in request_data or 'key' not in request_data or request_data['key'] != KEY:
        logger.error(f'Data not present or not valid: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Key not presented'
        return jsonify(answer)
    
    client_id = request_data['client_id']
    amount = request_data['amount']

    UpdateClientAmount().execute(client_id, amount)

    answer['data'] = 'ok'
    return jsonify(answer)
