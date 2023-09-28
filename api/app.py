from flask import Flask, jsonify
from flask_cors import CORS
import utils
from routes.client import client_api
from routes.peer import peer_api
from routes.pay import pay_api
from routes.actions import action_api

app = Flask(__name__)

app.register_blueprint(client_api)
app.register_blueprint(peer_api)
app.register_blueprint(pay_api)
app.register_blueprint(action_api)

CORS(app)

json_template = utils.json_template

 
@app.route('/api/v1.0/check', methods=['GET'])
def check():
    "Проверка связи"
    return jsonify(json_template)


if __name__ == '__main__':
    app.run(port=5001)
