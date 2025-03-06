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
    await message.reply(f'Инструкция по подключению моего ВПН:\n\n'
                        f'Для подключения вам потребуется приложение Hiddify. Если вы пользуетесь айфоном, то '
                        f'установите его из App Store, для всех остальных систем перейдите по <a '
                        f'href="https://github.com/hiddify/hiddify-app/releases/tag/v2.5.7">ссылке</a> выбрав вашу '
                        f'систему.\nЗатем отправьте этому боту команду /get которая сгенерирует для вас личную ссылку '
                        f'для подключения. Скопируйте её, а затем перейдите в приложение Hiddify, где нужно будет '
                        f'добавить профиль из буфера обмена. После этого в приложении вы можете свободно подключаться '
                        f'и отключаться от ВПН в любое время. По любым вопросам не стесняться обращаться к @mishin_iv'
                        f'\n\nОплата:\nДля поддержания сервера я беру по 150 рублей в месяц с каждого пользователя '
                        f'(либо больше, если вы хотите меня поддержать). Удобнее всего если вы настроете автоперевод '
                        f'раз в месяц по номеру +79775127643 (Иван Сергеевич Мишин).\n\nНесколько деталей:\n'
                        f'1. Теперь все ссылки на подключение индивидуальные и привязаны к вашему айди телеграма, '
                        f'поэтому если вы хотите поделиться ВПНом с кем-то другим, просто отправьте им этого бота, '
                        f'чтобы они сами получили уникальную ссылку.\n2. Для безопасности ВПНа, он работает только на '
                        f'сайты вне РФ, так что при заходе на русские сайты ВПН использоваться не будет, даже если он '
                        f'подключен в этот момент. Это сделано, чтобы сайты по типу Госуслуг не могли обнаружить, что '
                        f'вы используете ВПН и не заблокировали мой сервер.\n3. Все пользователи этого ВПНа используют '
                        f'один канал интернета, который делится между всеми, поэтому в моменты пиковой нагрузки '
                        f'скорость может и скорее всего будет просаживаться. Также, уважайте других пользователей и '
                        f'старайтесь по возможности не скачивать что-то очень объёмное через этот ВПН, чтобы не '
                        f'просаживать другим скорость в ноль.')


async def pbk_sid_handler():
        res = s.get(panel_url + 'panel/api/inbounds/list', verify=False)
        if res.history:
            login_handler()
            res = s.get(panel_url + 'panel/api/inbounds/list', verify=False)
        return (json.loads(res.json()['obj'][1]['streamSettings'])['realitySettings']['settings']['publicKey'],
                json.loads(res.json()['obj'][1]['streamSettings'])['realitySettings']['shortIds'][0])


@router.message(Command('get'))
async def get_handler(message: Message):
    template = {"id": 3, "settings": "{\"clients\": [{\"id\": \"" + f'{message.from_user.username}' + "\",\"flow\": \"xtls-rprx-vision\",\"email\": \"" + f'{message.from_user.username}' + "\",\"limitIp\": 0,\"totalGB\": 0,\"expiryTime\": 0,\"enable\": true,\"tgId\": \"" + f'{message.from_user.id}' + "\",\"subId\": \"286397\",\"reset\": 0}]}"}
    res = s.post(panel_url + 'panel/api/inbounds/addClient', data=template, verify=False)
    if res.history:
        login_handler()
        s.post(panel_url + 'panel/api/inbounds/addClient', data=template, verify=False)
    pbk, sid = await pbk_sid_handler()
    await message.reply(f'Ваша ссылка для подключения:\n<code>vless://{message.from_user.username}@{server_url}:443?'
                        f'type=tcp&security=reality&pbk={pbk}&fp=chrome&sni=modgen.nl&sid={sid}&spx=%2F&'
                        f'flow=xtls-rprx-vision#{message.from_user.username}</code>\n'
                        f'В приложении Hiddify выберите добавить подключение из буфера обмена, чтобы эта ссылка '
                        f'добавилась. При любых ошибках и неисправностях обращаться к @mishin_iv')


def login_handler():
    s.post(panel_url + 'login', verify=False, data={
        'username': config.panel_login.get_secret_value(),
        'password': config.panel_password.get_secret_value()})
