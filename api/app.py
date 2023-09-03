from flask import Flask, jsonify
from db.clients import GetClientById
from db.hosts import GetAllHosts
from db.peers import GetPeerByClientId, GetPeerById
from db.pay_history import GetClietnHistory

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

CONF_NAME = dashboard_config['config_name']

app = Flask(__name__)

json_template = {
    'status': True,
    'data': ''
}


 
@app.route('/api/v1.0/check', methods=['GET'])
def check():
    "Проверка связи"
    return jsonify(json_template)

@app.route('/api/v1.0/check_user/<int:user_id>', methods=['GET'])
def user_login_check(user_id: int):
    client = GetClientById().execute(user_id)
    answer = json_template.copy()

    answer['data'] = {'user_exist': True}
    if client is None:
        answer['data']['user_exist'] = False
    
    return jsonify(answer)
 
@app.route('/api/v1.0/region_list', methods=['GET'])
def region_list():
    regions = GetAllHosts().execute()
    regions = utils.get_permited_keys_from_dict_list(regions, ['id', 'region'])
    
    answer = json_template.copy()
    answer['data'] = regions
    return jsonify(answer)

@app.route('/api/v1.0/user/<int:client_id>', methods=['GET'])
def get_client(client_id: int):
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
    
    answer['data'] = {'amount': client['amount'], 'peers': client_peers}
    return jsonify(answer)

@app.route('/api/v1.0/bill_history/<int:client_id>', methods=['POST'])
def bill_history(client_id: int):
    bill_history = GetClietnHistory().execute(client_id)
    answer = json_template.copy()

    answer['data'] = {'bills': bill_history}
    return jsonify(answer)


@app.route('/api/v1.0/qrcode/', methods=['POST'])
def qrcode(client_id: int):
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