from flask import Blueprint, jsonify, request
from db.peers import GetPeerById
from db.pay_history import GetClietnHistory
from db.hosts import GetAllHosts
from db.clients import GetAllClients
from aiogram.types.input_file import BufferedInputFile
import asyncio
import configparser
from bot import send_file_to_user, send_mess_to_user
import utils
import os
import logging

action_api = Blueprint('action_api', __name__)
logger = logging.getLogger('gunicorn.error')

config = configparser.ConfigParser()
config.read('./config.ini')
MASS_KEY = str(config['sendmass']['key'])
BROADCAST_FILE = str(config['sendmass']['file'])


@action_api.route('/api/v1.0/region_list', methods=['GET'])
def region_list():
    "Получить список серверов"
    answer = utils.json_template.copy()

    regions = GetAllHosts().execute()
    regions = utils.get_permited_keys_from_dict_list(regions, ['id', 'region'])
    
    answer['data'] = regions
    return jsonify(answer)


@action_api.route('/api/v1.0/bill_history', methods=['POST'])
def bill_history():
    """получение чековой истории пользователя

    Args:
        client_id (int): id пользователя из телеги
    """
    logger.info('get bill history')
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data:
        logger.error(f'invalid params in bill_history: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Client id and host id not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])

    bill_history = GetClietnHistory().execute(client_id)
    for bill in bill_history:
        bill['create_date'] = bill['create_date'].strftime('%m.%d.%Y')
    bill_history.reverse()
    answer['data'] = {'bills': bill_history}

    return jsonify(answer)


@action_api.route('/api/v1.0/qrcode/', methods=['POST'])
def qrcode():
    """получение qr кода кнкретного подключения

    Args(POST):
        client_id (int): id пользователя из телеги
        host_id (int): id сервера из БД
    """
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'host_id' not in request_data:
        logger.error(f'invalid params in qrcode: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Client id and host id not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    host_id = int(request_data['host_id'])

    peer = GetPeerById().execute(client_id, host_id)
    if peer is None:
        logger.error(f'peer not found: client_id = {client_id}, host_id = {host_id}')
        raise InterruptedError("peer not exist")

    qrcode_str = utils.apis[host_id-1].qrcode('wg0', peer['params']['public_key'])
    answer['data'] = {'qrcode': qrcode_str}

    return jsonify(answer)


@action_api.route('/api/v1.0/download', methods=['POST'])
def download():
    """скачивание файла для подключения

    Args(POST):
        client_id (int): id пользователя из телеги
        host_id (int): id сервера из БД
    """
    logger.info('get download')
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'host_id' not in request_data:
        logger.error(f'invalid params in qrcode: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Client id and host id not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    host_id = int(request_data['host_id'])

    peer = GetPeerById().execute(client_id, host_id)
    if peer is None:
        logger.error(f'peer not found: client_id = {client_id}, host_id = {host_id}')
        raise InterruptedError("peer not exist")

    file = utils.apis[host_id-1].download('wg0', peer['params']['public_key'])
    if file is False:
        logger.error(f"file for peer not found: host_id = {host_id-1}, peer = {peer['params']['public_key']}")
        raise InterruptedError('can`t get file')
    file_content, file_title = file['content'], file['filename']
    file = bytes(file_content, 'utf-8')
    input_file = BufferedInputFile(file=file, filename=file_title)

    asyncio.run(send_file_to_user(client_id, input_file))

    answer['data'] = 'ok'
    return jsonify(answer)


@action_api.route('/api/v1.0/massmess/<key>', methods=['GET'])
def massmess(key: str):
    """отправка сообщения всем пользователям системы

    Args:
        key (str): ключ для отправки
    """
    answer = utils.json_template.copy()
    if key != MASS_KEY:
        answer['status'] = False
        answer['data'] = 'Invalid key for massmess'
        return jsonify(answer)
    
    if os.path.isfile(BROADCAST_FILE) is False:
        answer['status'] = False
        answer['data'] = 'File nor found'
        return jsonify(answer)
    
    with open(BROADCAST_FILE, 'r') as file:
        msg = file.readlines()
    
    msg = ''.join(msg)

    if len(msg.strip()) == 0:
        answer['status'] = False
        answer['data'] = 'File nor found'
        return jsonify(answer)
    
    user_list = GetAllClients().execute()

    for user in user_list:
        client_id = user['id']
        asyncio.run(send_mess_to_user(client_id, msg))
        
    answer['data'] = f'Message was send to {len(user_list)} users'

    return jsonify(answer)
