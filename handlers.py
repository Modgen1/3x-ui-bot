import requests
import json
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from config_reader import config

router = Router()
s = requests.Session()
admin_id = int(config.admin_id.get_secret_value())
panel_url = ('https://' + config.panel_host.get_secret_value() + ':' + config.panel_port.get_secret_value() +
             config.panel_uri_path.get_secret_value())
server_url = config.server_url.get_secret_value()


@router.message(Command('start'))
async def start_handler(message: Message):
    await message.reply(f'Тест {message.from_user.first_name}, {panel_url}')


async def pbk_sid_handler():
        res = s.get(panel_url + 'panel/api/inbounds/list', verify=False)
        if res.history:
            login_handler()
            res = s.get(panel_url + 'panel/api/inbounds/list', verify=False)
        return (json.loads(res.json()['obj'][0]['streamSettings'])['realitySettings']['settings']['publicKey'],
                json.loads(res.json()['obj'][0]['streamSettings'])['realitySettings']['shortIds'][0])


@router.message(Command('get'))
async def get_handler(message: Message):
    template = {"id": 1, "settings": "{\"clients\": [{\"id\": \"" + f'{message.from_user.username}' + "\",\"flow\": \"xtls-rprx-vision\",\"email\": \"" + f'{message.from_user.username}' + "\",\"limitIp\": 0,\"totalGB\": 0,\"expiryTime\": 0,\"enable\": true,\"tgId\": \"" + f'{message.from_user.id}' + "\",\"subId\": \"286397\",\"reset\": 0}]}"}
    res = s.post(panel_url + 'panel/api/inbounds/addClient', data=template, verify=False)
    if res.history:
        login_handler()
        s.post(panel_url + 'panel/api/inbounds/addClient', data=template, verify=False)
    pbk, sid = await pbk_sid_handler()
    await message.reply(f'Your connection link:\n<code>vless://{message.from_user.username}@{server_url}:443?type=tcp&'
                        f'security=reality&pbk={pbk}&fp=chrome&sni=modgen.nl&sid={sid}&spx=%2F&flow=xtls-rprx-vision#'
                        f'{message.from_user.username}</code>')


def login_handler():
    s.post(panel_url + 'login', verify=False, data={
        'username': config.panel_login.get_secret_value(),
        'password': config.panel_password.get_secret_value()})
