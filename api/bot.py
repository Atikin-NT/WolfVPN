from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TEST
from aiogram.enums.parse_mode import ParseMode
from utils import HELP_MSG, WELCOME_MSG, PEER_DELETE_MSG
import configparser
import logging
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
BROADCAST_FILE = 'msg.txt'

logger = logging.getLogger('gunicorn.error')


async def send_file_to_user(client_id, input_file):
    logger.info(f'sent file to user where client_id = {client_id}, is_test={is_test}')
    await bot.session.close()
    await bot.send_document(client_id, document=input_file)


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


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    webapp = types.WebAppInfo(url="https://wolfvpn.ru")
    builder.add(types.InlineKeyboardButton(
        text="WolfVPN WebApp", web_app=webapp),
    )
    await message.answer(
        WELCOME_MSG,
        reply_markup=builder.as_markup()
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        HELP_MSG,
        parse_mode=ParseMode.HTML
    )


async def send_mess_to_user(client_id: int, text: str):
    await bot.session.close()
    await bot.send_message(
        chat_id=client_id,
        text=text
    )


@dp.message(Command("create_mess"))
async def broadcast(message: types.Message):
    msg_without_command = message.html_text.replace('/create_mess', '')
    clear_msg = msg_without_command.strip()
    
    with open(BROADCAST_FILE, 'w') as file:
        file.write(clear_msg)
    
    await message.answer('Сообщение сохранено')


@dp.message(Command("show_mess"))
async def broadcast(message: types.Message):
    if os.path.isfile(BROADCAST_FILE) is False:
        await message.answer('Файл сообщений отсутсвует')
        return
    
    with open(BROADCAST_FILE, 'r') as file:
        msg = file.readlines()
    
    msg = ''.join(msg)

    if len(msg.strip()) == 0:
        await message.answer('Файл сообщений пустой')
        return
    
    await message.answer(msg, parse_mode=ParseMode.HTML)


async def run_bot():
    await dp.start_polling(bot)


def main():
    logger.info(f'run bot PID = {os.getpid()}, PPID = {os.getppid()}')
    asyncio.run(run_bot())

# https://telegra.ph/WolfVPN-Tutorial-11-30
