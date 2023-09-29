import time
import schedule
from db.clients import GetAllClients, UpdateClientAmount
from db.peers import GetPeerByClientId, RemovePeer
import utils
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')
DAY_PAY = int(config['economic']['day_pay'])


def remove_peer(client_id: int, host_id: int, pubkey: str):
    res = utils.apis[host_id-1].remove_peer('wg0', [pubkey])
    if res is False:
        raise InterruptedError("Can't remove")
    RemovePeer().execute(client_id, host_id)


def debit():
    user_list = GetAllClients().execute()
    for user in user_list:
        client_id = user['id']
        amount = user['amount']

        if amount <= 0: continue

        peers = GetPeerByClientId().execute(client_id)
        peer_count = len(peers)

        for i in range(peer_count):
            peer = peers[i]
            if DAY_PAY > amount:
                try:
                    remove_peer(client_id, int(peer['host_id']), peer['params']['public_key'])
                except Exception as msg:
                    pass
            amount -= DAY_PAY

        amount = 0 if amount < 0 else amount
        UpdateClientAmount().execute(client_id, amount)


def auto_daily_debit():
    schedule.every().seconds.do(debit)
    while True:
        schedule.run_pending()
        time.sleep(1)