from flask import Flask, jsonify
from db.clients import GetClientById
from db.hosts import GetAllHosts

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
    permited_keys = ['id', 'region']
    regions = [{key: region[key]
                for key in region if key in permited_keys} 
                for region in regions]

    answer = json_template.copy()
    answer['data'] = regions
    return jsonify(answer)

if __name__ == '__main__':
    app.run(port=5001)