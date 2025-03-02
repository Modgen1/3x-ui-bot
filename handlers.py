import requests
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config_reader import config

router = Router()
s = requests.Session()
admin_id = int(config.admin_id.get_secret_value())
panel_url = ('https://' + config.panel_host.get_secret_value() + ':' + config.panel_port.get_secret_value() +
             config.panel_uri_path.get_secret_value())


@router.message(Command('start'))
async def start_handler(message: Message):
    await message.reply(f'Тест {message.from_user.first_name}, {panel_url}')


@router.message(Command('list'))
async def start_handler(message: Message):
    if message.from_user.id == admin_id:
        res = s.get(panel_url + 'panel/api/inbounds/list', verify=False)
        if res.history:
            login_handler()
            res = s.get(panel_url + 'panel/api/inbounds/list', verify=False)
        await message.reply(f'{res.json()}')


def login_handler():
    s.post(panel_url + 'login', verify=False, data={
        'username': config.panel_login.get_secret_value(),
        'password': config.panel_password.get_secret_value()})
