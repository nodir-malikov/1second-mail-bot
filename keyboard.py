from aiogram import types

menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    types.KeyboardButton('✉️ Получить почту')
)
