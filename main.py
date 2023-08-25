import logging
import aiogram
import configparser
from db.clients import AddClietn

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
    AddClietn().execute(client_id=123, name='123')
    logging.info("test")
