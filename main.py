import logging

from aiogram import Bot, Dispatcher, executor, types

from config import API_TOKEN, EMAIL_DOMAIN
import keyboard as kb
from onesec_api import Mailbox
import asyncio
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(content_types=['text'])
async def texthandler(m: types.Message):
    if m.text != '✉️ Получить почту':
        await m.answer(
            f'Приветствую тебя, {m.from_user.mention}\nЭтот бот создан для быстрого получения временной почты.\nНажми '
            f'на кнопу ниже 👇',
            reply_markup=kb.menu)
    elif m.text == '✉️ Получить почту':
        mail = Mailbox('')
        email = f'{mail.mailbox_}@{EMAIL_DOMAIN}'
        await m.answer(
            f'📫 Вот твоя почта: {email}\nОтправляй письмо.\nПочта проверяется автоматически, каждые 5 секунд, '
            f'если придет новое письмо, мы вас об этом оповестим!\nНа 1 почту можно получить только - 1 письмо.\nНаш '
            f'канал @slivmens')

        last_length = 0
        while True:
            filtered_mail = mail.filtered_mail()
            if isinstance(filtered_mail, list):
                if last_length == len(filtered_mail):
                    pass
                else:
                    last_length = len(filtered_mail)

                    new_mail = mail.mail_jobs('read', filtered_mail[0])

                    js = new_mail.json()
                    sender = js['from']
                    theme = js['subject']
                    mes = js['body']
                    cleantext = BeautifulSoup(mes, "html.parser")
                    cleantext = "\n".join(item.strip() for item in cleantext.find_all(text=True))
                    await m.answer(
                        f'📩 Новое письмо:\n<b>От</b>: {sender}\n'
                        f'<b>Тема</b>: {theme}\n<b>Сообщение</b>: \n\n{cleantext}',
                        reply_markup=kb.menu, parse_mode='HTML')

            await asyncio.sleep(1)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
