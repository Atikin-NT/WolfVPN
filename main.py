import logging
import aiogram
import configparser
from wireguard.api import API

config = configparser.ConfigParser()
config.read('./config.ini')
bot_config = config['bot']
dashboard_config = config['dashboard']
BASE_URL = dashboard_config['base_url']
LOGIN_URL = dashboard_config['login_url']
LOGIN = dashboard_config['login']
PASSWORD = dashboard_config['password']

if __name__ == '__main__':
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        filemode="w"
    )
    api = API(PASSWORD, LOGIN, LOGIN_URL, BASE_URL)
    r, peer = api.add_peer('wg0', {'username': 'get_exist_peer_data'})
    assert r == True

    r = api.get_peer_data('wg0', peer['public_key'])
    print(r)
    assert r['public_key'] == peer['public_key']
    logging.info("test")
