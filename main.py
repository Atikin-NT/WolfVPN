import logging
import aiogram
import configparser
from db.clients import AddClietn
from db.pay_history import AddBill
from db.init import CreateTable

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
    CreateTable().execute()
    logging.info("test")
