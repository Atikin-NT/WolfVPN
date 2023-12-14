import time
import datetime
from db.clients import GetAllClients, UpdateClientAmount
from db.peers import GetPeerByClientId, RemovePeer
from db.db_manager import Connection, DataBaseManager
import utils
import configparser
import logging
from logging.handlers import QueueHandler
from wireguard.api import API
import os

config = configparser.ConfigParser()
config.read('./config.ini')
DAY_PAY = int(config['economic']['day_pay'])
db_config = config['database']


def remove_peer(api: API, client_id: int, host_id: int, pubkey: str):
    logging.info(f'delete peer: client_id = {client_id}, host_id = {host_id}, PID = {os.getpid()}')
    res = api.remove_peer('wg0', [pubkey])
    if res is False:
        raise InterruptedError("Can't remove")
    RemovePeer().execute(client_id, host_id)


def debit(api_list):
    user_list = GetAllClients().execute()
    for user in user_list:
        client_id = user['id']
        amount = user['amount']

        peers = GetPeerByClientId().execute(client_id)
        peer_count = len(peers)
        logging.info(f'update user balance/ User={client_id}, amount={amount}, PID = {os.getpid()}')

        if peer_count <= 0: continue

        for i in range(peer_count):
            peer = peers[i]
            host_id = int(peer['host_id'])
            if DAY_PAY > amount:
                try:
                    remove_peer(api_list[host_id-1], client_id, host_id, peer['params']['public_key'])
                except Exception as e:
                    logging.error(f'Error in debit function. Ex = {e}')
            amount -= DAY_PAY

        amount = 0 if amount < 0 else amount
        UpdateClientAmount().execute(client_id, amount)
        logging.info(f'new user balance/ User={client_id}, amount={amount}, PID = {os.getpid()}')


def auto_daily_debit(mp_queue):
    queue_handler = QueueHandler(mp_queue)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(queue_handler)
    logging.info(f'run database PID = {os.getpid()}, PPID = {os.getppid()}')
    Connection.db = DataBaseManager(db_config['dbname'], db_config['user'], db_config['password'])

    while True:
        curr_time = datetime.datetime.now()
        if curr_time.hour < 1:
            debit(utils.apis)
            time.sleep(60*60)
        time.sleep(60*20)