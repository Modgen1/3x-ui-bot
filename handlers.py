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
    await message.reply(f'📌Инструкция по подключению моего ВПН:\n\n'
                        f'Для подключения вам потребуется приложение Hiddify.\n- Если вы пользуетесь айфоном, то '
                        f'установите его из App Store, для всех остальных систем перейдите по <a '
                        f'href="https://github.com/hiddify/hiddify-app/releases/tag/v2.5.7">ссылке</a> и скачайте, '
                        f'выбрав вашу систему.\n- Затем отправьте этому боту команду /get, которая сгенерирует для вас '
                        f'личную ссылку для подключения.\n- Скопируйте её, а затем перейдите в приложение Hiddify, где '
                        f'нужно будет добавить профиль из буфера обмена.\n\nПосле этого в приложении вы можете свободно'
                        f' подключаться и отключаться от ВПН в любое время.\n\n💌По любым вопросам не стесняться '
                        f'обращаться к @mishin_iv\n\n💸Оплата:\nДля поддержания сервера я беру по 150 рублей в месяц с '
                        f'каждого пользователя (либо больше, если вы хотите меня поддержать). Удобнее всего если вы '
                        f'настроете автоперевод раз в месяц по номеру +79775127643 (Иван Сергеевич Мишин).\n\n✍️'
                        f'Несколько деталей:\n1. Теперь все ссылки на подключение индивидуальные и привязаны к вашему '
                        f'айди телеграма, поэтому если вы хотите поделиться ВПНом с кем-то другим, просто отправьте им '
                        f'этого бота, чтобы они сами получили уникальную ссылку.\n2. Для безопасности ВПНа, он работает'
                        f' только на сайты вне РФ, так что при заходе на русские сайты ВПН использоваться не будет, '
                        f'даже если он подключен в этот момент. Это сделано, чтобы сайты по типу Госуслуг не могли '
                        f'обнаружить, что вы используете ВПН и не заблокировали мой сервер.\n3. Все пользователи этого '
                        f'ВПНа используют один канал интернета, который делится между всеми, поэтому в моменты пиковой '
                        f'нагрузки скорость может и скорее всего будет просаживаться.\n\nТакже, уважайте других '
                        f'пользователей и старайтесь по возможности не скачивать что-то очень объёмное через этот ВПН, '
                        f'чтобы не просаживать другим скорость в ноль.')


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
    await message.reply(f'Ваша ссылка для подключения:\n<pre>vless://{message.from_user.username}@{server_url}:443?'
                        f'type=tcp&security=reality&pbk={pbk}&fp=chrome&sni=modgen.nl&sid={sid}&spx=%2F&'
                        f'flow=xtls-rprx-vision#{message.from_user.username}</pre>\n'
                        f'В приложении Hiddify выберите добавить подключение из буфера обмена, чтобы эта ссылка '
                        f'добавилась. При любых ошибках и неисправностях обращаться к @mishin_iv')


def login_handler():
    s.post(panel_url + 'login', verify=False, data={
        'username': config.panel_login.get_secret_value(),
        'password': config.panel_password.get_secret_value()})
