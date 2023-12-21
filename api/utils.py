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

WELCOME_MSG = """
Привет!
Рады приветствовать тебя в нашем VPN сервисе 🚀🚀🚀

Это тебе может пригодиться:
/start - главное меню с ссылкой на бота
/help - краткая инструкция по подключению
@wolf0vpn_help_bot - по всем вопросам и пожеланиям.

Хватит разговоров, скорее запуская приложение ⬇️⬇️⬇️
"""

HELP_MSG = """
Если вы не знаете, как подключить VPN, то следуйте следующей инструкции:
1) Скачайте Wireguard.
    <a href="https://itunes.apple.com/us/app/wireguard/id1441195209?ls=1&mt=8">IOS</a>
    <a href="https://play.google.com/store/apps/details?id=com.wireguard.android">Android</a>
    <a href="https://download.wireguard.com/windows-client/wireguard-installer.exe">Windows</a>
2) Скачайте файл для подключения в нашем боте.
3) Откройте его в приложении Wireguard.
4) Приятного пользования! 

Если же у вас возникли вопросы или что-то не получается, то вот <a href="https://telegra.ph/WolfVPN-Tutorial-11-30">тут</a> находится более подробная инструкция.

Или можете написать прямо нам, мы поможем: @wolf0vpn_help_bot
"""

REMINDER_MSG = """
Напоминаем, у вас на счету осталось <code>{val} W</code>, этого хватит на <code>{days} {day_text}</code>

Незабудьте пополнить счет, иначе ваще подключение автоматически удалится!
"""

PEER_DELETE_MSG = """
Ваше подключение было удалено! В приложении вы можете получить новое подключение, пополнив счет.
"""
