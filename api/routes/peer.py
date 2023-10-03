from flask import Blueprint, jsonify, request
from db.peers import GetPeerById, AddPeer, RemovePeer
import db.exeption as ex
import utils

peer_api = Blueprint('peer_api', __name__)


@peer_api.route('/api/v1.0/add_peer', methods=['POST'])
def add_peer():
    """добавить новое подключение

    Args:
        client_id (int): id пользователя из телеги
        host_id (int): id хоста
        username (str): ник пользователя
    """
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'username' not in request_data or 'client_id' not in request_data or 'host_id' not in request_data:
        answer['status'] = False
        answer['data'] = 'Not all values was presented'
        return jsonify(answer)
    client_id = request_data['client_id']
    host_id = int(request_data['host_id'])
    answer['data'] = 'ok'

    try:
        data, params = utils.apis[host_id-1].add_peer('wg0', request_data)
        AddPeer().execute(client_id, host_id, params)
    except (ex.HostOrUserNotExist, ex.PeerAlreadyExist) as e:
        answer['status'] = False
        answer['data'] = e
    
    return jsonify(answer)


@peer_api.route('/api/v1.0/remove_peer', methods=['POST'])
def remove_peer():
    """добавить новое подключение

    Args:
        client_id (int): id пользователя из телеги
        host_id (int): id хоста
    """
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'host_id' not in request_data:
        answer['status'] = False
        answer['data'] = 'Not all values was presented'
        return jsonify(answer)
    client_id = request_data['client_id']
    host_id = int(request_data['host_id'])

    peer = GetPeerById().execute(client_id, host_id)
    if peer is None:
        raise InterruptedError("peer not exist")
    res = utils.apis[host_id-1].remove_peer('wg0', [peer['params']['public_key']])
    if res is False:
        raise InterruptedError("Can't remove")
    RemovePeer().execute(client_id, host_id)
    
    answer['data'] = 'ok'
    return jsonify(answer)