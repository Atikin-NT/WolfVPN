from wireguard.api import API
import configparser

config = configparser.ConfigParser()
config.read('./config.ini')
dashboard_config = config['dashboard']

json_template = {
    'status': True,
    'data': ''
}

def get_permited_keys_from_dict_list(d: list, keys: list) -> list:
    r = [{key: i[key]
                for key in i if key in keys} 
                for i in d]
    return r


def dict_search(d: list, key_s: str, val_s: any, key_r: str) -> any:
    for i in d:
        if i[key_s] == val_s:
            return i[key_r]
    return None


def create_ini_config_list(d: dict):
    confs = []
    for key in d.keys():
        d[key] = d[key].split(',')

    for i in range(len(d['base_url'])):
        confs.append({
            'base_url': d['base_url'][i],
            'login_url': d['login_url'][i],
            'login': d['login'][i],
            'password': d['password'][i],
            'config_name': d['config_name'][i],
        })

    return confs

all_confs = create_ini_config_list(dict(dashboard_config))
apis = []
for conf in all_confs:
    apis.append(API(
        conf['password'],
        conf['login'],
        conf['login_url'],
        conf['base_url']
    ))