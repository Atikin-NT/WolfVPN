import time
import datetime
import bot
import asyncio
import utils
import configparser
import logging
import api
import os

config = configparser.ConfigParser()
config.read('./config.ini')
DAY_PAY = int(config['economic']['day_pay'])


def remove_peer(client_id: int, host_id: int):
    logging.info(f'delete peer: client_id = {client_id}, host_id = {host_id}, PID = {os.getpid()}')
    op_status = api.remove_peer(client_id, host_id)
    if op_status is False:
        logging.error("Can't remove")
        return
    
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


def debit():
    user_list = api.get_all_clients_list()
    for user in user_list:
        client_id = user['id']
        amount = user['amount']

        peers = user['peers']
        peer_count = len(peers)
        logging.info(f'update user balance/ User={client_id}, amount={amount}, PID = {os.getpid()}')

        if peer_count <= 0: continue

        for i in range(peer_count):
            peer = peers[i]
            host_id = int(peer['host_id'])
            if DAY_PAY > amount:
                try:
                    remove_peer(client_id, host_id)
                except Exception as e:
                    logging.error(f'Error in debit function. Ex = {e}')
            amount -= DAY_PAY

        amount = 0 if amount < 0 else amount

        send_reminder_by_bot(client_id, amount, peer_count)

        api.update_client_amount(client_id, amount)
        logging.info(f'new user balance/ User={client_id}, amount={amount}, PID = {os.getpid()}')


def main():
    while True:
        curr_time = datetime.datetime.now()
        if curr_time.hour < 1:
            debit()
            time.sleep(60*60)
        time.sleep(60*20)


if __name__ == "__main__":
    logging.basicConfig(filename="debit.log",
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        filemode="w")
    logging.info(f'run debit PID = {os.getpid()}, PPID = {os.getppid()}')
    main()
