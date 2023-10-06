from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TEST
import configparser
import logging

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


async def send_file_to_user(client_id, input_file):
    logging.info(f'sent file to user where client_id = {client_id}')
    await bot.session.close()
    await bot.send_document(client_id, document=input_file)
