from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TEST
from aiogram.enums.parse_mode import ParseMode
from utils import HELP_MSG, WELCOME_MSG
import configparser
import logging
from logging.handlers import QueueHandler
import asyncio
import os

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
dp = Dispatcher()


async def send_file_to_user(client_id, input_file):
    logging.info(f'sent file to user where client_id = {client_id}, is_test={is_test}')
    await bot.session.close()
    await bot.send_document(client_id, document=input_file)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    webAppTest = types.WebAppInfo(url="https://wolfvpn.ru")
    builder.add(types.InlineKeyboardButton(
        text="WolfVPN WebApp", web_app=webAppTest),
    )
    await message.answer(
        WELCOME_MSG,
        reply_markup=builder.as_markup()
    )

@dp.message(Command("help"))
async def cmd_start(message: types.Message):
    await message.answer(
        HELP_MSG,
        parse_mode=ParseMode.HTML
    )

async def run_bot():
    await dp.start_polling(bot)


def main(mp_queue):
    queue_handler = QueueHandler(mp_queue)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(queue_handler)
    logging.info(f'run bot PID = {os.getpid()}, PPID = {os.getppid()}')
    asyncio.run(run_bot())

# https://telegra.ph/WolfVPN-Tutorial-11-30
