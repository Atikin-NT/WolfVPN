from flask import Blueprint, jsonify, request
from db.clients import GetClientById, AddClient, UpdateClientAmount
from db.peers import GetPeerByClientId
from db.hosts import GetAllHosts
import db.exeption as ex
import utils
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')
DAY_PAY = int(config['economic']['day_pay'])

client_api = Blueprint('client_api', __name__)


@client_api.route('/api/v1.0/check_user/<int:user_id>', methods=['GET'])
def user_login_check(user_id: int):
    """Проверка на наличие пользователя в системе

    Args:
        user_id (int): id пользователя из телеги
    """
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
    answer = utils.json_template.copy()
    request_data = request.get_json()

    if 'client_id' not in request_data or 'name' not in request_data:
        answer['status'] = False
        answer['data'] = 'Client id and name not presented'
        return jsonify(answer)

    client_id = request_data['client_id']
    name = request_data['name']

    try:
        AddClient().execute(client_id, name)
    except (ValueError, ex.ClientAlreadyExist) as e:
        answer['status'] = False
        answer['data'] = e

    return jsonify(answer)

@client_api.route('/api/v1.0/user/<int:client_id>', methods=['GET'])
def get_client(client_id: int):
    """получение информации о пользователе

    Args:
        client_id (int): id пользователя из телеги
    """
    answer = utils.json_template.copy()

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
