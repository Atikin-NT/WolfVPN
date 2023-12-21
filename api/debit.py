import time
import datetime
from db.clients import GetAllClients, UpdateClientAmount
from db.peers import GetPeerByClientId, RemovePeer
from db.db_manager import Connection, DataBaseManager
import bot
import asyncio
import utils
import configparser
import logging
from wireguard.api import API
import os

config = configparser.ConfigParser()
config.read('./config.ini')
DAY_PAY = int(config['economic']['day_pay'])
db_config = config['database']


def remove_peer(api: API, client_id: int, host_id: int, pubkey: str, logger: logging.Logger):
    logger.info(f'delete peer: client_id = {client_id}, host_id = {host_id}, PID = {os.getpid()}')
    res = api.remove_peer('wg0', [pubkey])
    if res is False:
        raise InterruptedError("Can't remove")
    RemovePeer().execute(client_id, host_id)
    asyncio.run(bot.delete_mess(client_id))


def send_reminder_by_bot(client_id: int, amount: int, peer_count: int):
    day_left = amount // (DAY_PAY * peer_count)
    if day_left > 3 or day_left <= 0:
        return
    
    day_text = {
        '1': 'день',
        '2': 'дня',
        '3': 'дня'
    }

    msg = utils.REMINDER_MSG
    msg = msg.format(
        val = amount,
        days = day_left,
        day_text = day_text[f'{day_left}']
    )
    asyncio.run(bot.send_reminder(client_id, msg))


def debit(api_list, logger):
    user_list = GetAllClients().execute()
    for user in user_list:
        client_id = user['id']
        amount = user['amount']

        peers = GetPeerByClientId().execute(client_id)
        peer_count = len(peers)
        logger.info(f'update user balance/ User={client_id}, amount={amount}, PID = {os.getpid()}')

        if peer_count <= 0: continue

        for i in range(peer_count):
            peer = peers[i]
            host_id = int(peer['host_id'])
            if DAY_PAY > amount:
                try:
                    remove_peer(api_list[host_id-1], client_id, host_id, peer['params']['public_key'], logger)
                except Exception as e:
                    logger.error(f'Error in debit function. Ex = {e}')
            amount -= DAY_PAY

        amount = 0 if amount < 0 else amount

        send_reminder_by_bot(client_id, amount, peer_count)

        UpdateClientAmount().execute(client_id, amount)
        logger.info(f'new user balance/ User={client_id}, amount={amount}, PID = {os.getpid()}')


def auto_daily_debit():
    logger = logging.getLogger('gunicorn.error')
    logger.info(f'run database PID = {os.getpid()}, PPID = {os.getppid()}')
    Connection.db = DataBaseManager(db_config['dbname'], db_config['user'], db_config['password'])

    while True:
        curr_time = datetime.datetime.now()
        if curr_time.hour < 1:
            debit(utils.apis, logger)
            time.sleep(60*60)
        time.sleep(60*20)