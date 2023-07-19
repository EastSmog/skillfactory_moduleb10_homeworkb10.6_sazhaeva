import telebot
from telebot import types
from cr_config import keys, TOKEN
from cr_utils import ConvertionException, CryptoConverter

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    text1 = None
    if message.chat.first_name is not None and message.chat.last_name is not None:
        text1 = f"Здравствуйте, {message.chat.first_name} {message.chat.last_name}!"
    elif message.chat.first_name is not None:
        text1 = f"Здравствуйте, {message.chat.first_name}!"
    elif message.chat.last_name is not None:
        text1 = f"Здравствуйте, {message.chat.last_name}!"
    text2 = 'Добро пожаловать в бот, конвертирующий валюты. \n' \
            'Увидеть список всех доступных валют: /values \n' \
            'Чтобы начать работу, выберете из предложенных валюту, которую Вы хотите конвертировать'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    btns = set()
    for key in keys.keys():
        btn = types.KeyboardButton(key)
        btns.add(btn)
    markup.add(*btns)
    bot.send_message(message.chat.id, '\n'.join((text1, text2)).format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text, key,))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def first_value(message: telebot.types.Message):
    in_values = message.text
    text = 'Выберете валюту конвертации'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    btns = set()
    for key in keys.keys():
        btn = types.KeyboardButton(key)
        btns.add(btn)
    markup.add(*btns)
    bot.send_message(message.chat.id, text.format(message.from_user), reply_markup=markup)
    bot.register_next_step_handler(message, second_value, in_values)
    return in_values


def second_value(message: telebot.types.Message, in_values):
    in_values += ' ' + message.text
    text = 'Введите количество конвертируемой валюты'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, convert, in_values)
    return in_values


def convert(message: telebot.types.Message, in_values):
    in_values += ' ' + message.text
    try:
        in_values = in_values.split(' ')
        if len(in_values) != 3:
            raise ConvertionException('Необходимо ввести три параметра')

        quote, base, amount = in_values
        total_base = CryptoConverter.convert(quote, base, amount)
    except ConvertionException as e:
        bot.reply_to(message, f'Ошибка пользователя\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        text = f'Цена {amount} {quote} в {base} - {total_base}'
        bot.send_message(message.chat.id, text)


bot.polling()
