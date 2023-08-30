from flask import Flask, jsonify
from db.clients import GetClientById
from db.hosts import GetAllHosts
from db.peers import GetPeerByClientId
import utils

app = Flask(__name__)

json_template = {
    'status': True,
    'data': ''
}
 
@app.route('/api/v1.0/check', methods=['GET'])
def check():
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
    client = GetClientById().execute(client_id)
    answer = json_template.copy()

    client_peers = GetPeerByClientId().execute(client_id)
    client_peers = utils.get_permited_keys_from_dict_list(client_peers, ['client_id', 'host_id'])
    
    regions = GetAllHosts().execute()
    regions = utils.get_permited_keys_from_dict_list(regions, ['id', 'region'])

    client_peers = [peer | {'region': utils.dict_search(regions, 'id', peer['host_id'], 'region')}
                    for peer in client_peers]
    
    answer['data'] = {'amount': client['amount'], 'peers': client_peers}
    return jsonify(answer)

if __name__ == '__main__':
    app.run(port=5001)