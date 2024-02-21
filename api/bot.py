from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TEST
from aiogram.enums.parse_mode import ParseMode
import configparser
import logging

config = configparser.ConfigParser()
config.read('./config.ini')
is_test = True if config['settings']['is_test'] == 'True' else False

if is_test:
    bot_config = config['bot-test']
    session = AiohttpSession(
        api=TEST
    )
else:
    bot_config = config['bot']
    session = None

TOKEN = bot_config['key']
bot = Bot(token=TOKEN, session=session)

logger = logging.getLogger('gunicorn.error')


async def send_file_to_user(client_id, input_file):
    logger.info(f'sent file to user where client_id = {client_id}, is_test={is_test}')
    await bot.session.close()
    await bot.send_document(client_id, document=input_file)


async def send_mess_to_user(client_id: int, text: str):
    await bot.session.close()
    await bot.send_message(
        chat_id=client_id,
        text=text,
        parse_mode=ParseMode.HTML
    )

# https://telegra.ph/WolfVPN-Tutorial-11-30
