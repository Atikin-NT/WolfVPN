from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TEST

import configparser
config = configparser.ConfigParser()
config.read('./config.ini')
bot_config = config['bot-test']

is_test = bot_config['is_test']
TOKEN = bot_config['key']

if is_test:
    session = AiohttpSession(
        api=TEST
    )
else:
    session = None


bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()
