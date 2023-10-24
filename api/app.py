from flask import Flask, jsonify
from flask_cors import CORS
import utils
import flask_monitoringdashboard as dashboard
from routes.client import client_api
from routes.peer import peer_api
from routes.pay import pay_api
from routes.actions import action_api
from db.db_manager import Connection, DataBaseManager
from db.init import CreateTable
import debit
import multiprocessing as mp
import configparser
import logging

config = configparser.ConfigParser()
config.read('./config.ini')
db_config = config['database']

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


dashboard.bind(app)

def preload():
    logging.basicConfig(filename="app.log",
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        filemode="w")
    logging.info('Start wolfvpn')
    
    p = mp.Process(target=debit.auto_daily_debit, daemon=True)
    p.start()

    Connection.db = DataBaseManager(db_config['dbname'], db_config['user'], db_config['password'])
    CreateTable().execute()

preload()


if __name__ == '__main__':
    app.run(port=5001)
