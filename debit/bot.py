from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TEST
from aiogram.enums.parse_mode import ParseMode
from utils import PEER_DELETE_MSG
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


async def send_reminder(client_id: int, text: str):
    builder = InlineKeyboardBuilder()
    webapp = types.WebAppInfo(url="https://wolfvpn.ru/pay")
    builder.add(types.InlineKeyboardButton(
        text="Пополнить счет", web_app=webapp),
    )
    await bot.session.close()
    await bot.send_message(
        chat_id=client_id,
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )


async def delete_mess(client_id: int):
    builder = InlineKeyboardBuilder()
    webapp = types.WebAppInfo(url="https://wolfvpn.ru/pay")
    builder.add(types.InlineKeyboardButton(
        text="Пополнить счет", web_app=webapp),
    )
    await bot.session.close()
    await bot.send_message(
        chat_id=client_id,
        text=PEER_DELETE_MSG,
        reply_markup=builder.as_markup()
    )

# https://telegra.ph/WolfVPN-Tutorial-11-30
