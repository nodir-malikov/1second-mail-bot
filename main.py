import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from config import API_TOKEN, EMAIL_DOMAIN
from custom_funcs import set_timer
import keyboard as kb
from onesec_api import Mailbox
import asyncio
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(content_types=['text'], state='*')
async def texthandler(m: types.Message, state: FSMContext):
    if m.text != '✉️ Получить почту':
        await m.answer(
            f'Приветствую вас, {m.from_user.mention}\nЭтот бот создан для быстрого получения временной почты.\nНажмите '
            f'на кнопу ниже 👇',
            reply_markup=kb.menu)
    elif m.text == '✉️ Получить почту':
        has_mail = await state.get_data()
        try:
            if has_mail['has_mail']:
                await m.answer(f"✉️ У вас уже есть активная почта - {has_mail['email']}\nЖдите окончания лимитов...")
        except Exception:
            mail = Mailbox('')
            email = f'{mail.mailbox_}@{EMAIL_DOMAIN}'
            await m.answer(
                f'📫 Вот ваша почта: {email}\nОтправляйте письмо.\n'
                f'Почта проверяется автоматически, каждые 5 секунд, '
                f'если придет новое письмо, мы вас об этом оповестим!\n'
                f'На 1 почту можно получить только - 5 писем за 3 '
                f'минуты времени.\n\n '
                f'@mal1kov', reply_markup=ReplyKeyboardRemove())
            await state.update_data(has_mail=True)
            await state.update_data(email=email)

            last_length = 0
            now = datetime.now()
            end_time = now + timedelta(minutes=3)
            while True:
                now = datetime.now()
                timed_out = await set_timer(now, end_time)
                if last_length >= 5 or timed_out:
                    await m.answer('Лимиты этой почты закончились. ⌛️ \nСпасибо за использование! 👍 \n\nСказать '
                                   'спасибо 👉 <a href="https://www.donationalerts.com/r/phantom_donat">Донат</a> '
                                   '\n\nНажмите на кнопу ниже, чтобы получить новую временную '
                                   'почту 👇', reply_markup=kb.menu, parse_mode='HTML')
                    await state.finish()
                    break

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
                            f'📩 Новое письмо:\n'
                            f'<b>От</b>: {sender}\n'
                            f'<b>Тема</b>: {theme}\n'
                            f'<b>Сообщение</b>: \n\n{cleantext}', parse_mode='HTML')

                await asyncio.sleep(5)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
