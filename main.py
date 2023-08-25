import logging
import aiogram
import configparser
from db.clients import AddClietn
from db.pay_history import AddBill

config = configparser.ConfigParser()
config.read('./config.ini')
bot_config = config['bot']

if __name__ == '__main__':
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        filemode="w"
    )
    # AddClietn().execute(client_id=123, name='123')
    AddBill().execute(client_id=123, amount=1)
    logging.info("test")
