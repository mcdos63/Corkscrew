import telebot
import time
from datetime import datetime
import random
from telebot import types

with open('doc/bot.txt', 'r') as file:
    bot_id = file.readlines()
bot = telebot.TeleBot(*bot_id)
file_path = 'doc/facts.txt'
time_open = 12
time_close = 1

# Словарь для перевода дней недели на русский язык
days_of_week_ru = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье"
}

# Получение текущего дня недели и времени
now = datetime.now()
day_of_week = days_of_week_ru[now.strftime("%A")]  # Получаем день недели на русском
current_time = now.strftime("%H:%M")  # Текущее время
current_hour = int(current_time.split(':')[0])

start_text = (
    f'<b>Сегодня прекрасный день! {day_of_week}, время {current_time}.</b>\n'
    f"{"Двери буфета пока закрыты, но мы готовимся принять Вас у нас в рабочее время." if time_close<=current_hour<=time_open else 'Двери буфета открыты. Ждём только вас, приходите скорее!'}\n"
    f"В буфете <b>\"Штопор\"</b> вы можете насладиться разнообразными закусками и напитками на любой вкус. \n"
    f"<i>У нас приятный интерьер, доброжелательные сотрудники и большое разнообразие блюд для всех возрастов!</i>\n"
)
@bot.message_handler(commands=['start'])
def start_message(message):
    sti = open('doc/s.png', 'rb')
    bot.send_sticker(message.chat.id, sti, message_effect_id='5046509860389126442')

    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!'.format(message.from_user))
    bot.send_message(message.chat.id, start_text, parse_mode='HTML')

    # Создание inline-клавиатуры
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('Режим работы', callback_data='working_hours')
    btn2 = types.InlineKeyboardButton('Как нас найти', callback_data='find_us')
    btn3 = types.InlineKeyboardButton('Меню', callback_data='menu')
    btn4 = types.InlineKeyboardButton('Интересные факты', callback_data='fact')
    btn5 = types.InlineKeyboardButton('Фотогалерея', callback_data='photo_gallery')
    btn6 = types.InlineKeyboardButton('Отправить сообщение', callback_data='send_message')

    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)

def send_random_fact(chat_id):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.read().split('\n')
            random_fact = random.choice(lines)
            bot.send_message(chat_id, f'{random_fact}')
    except Exception as e:
        return f"Ошибка при чтении файла: {e}"

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'working_hours':
        bot.send_message(call.message.chat.id, f"Наш режим работы: {time_open}:00 - {time_close:02}:00")
    elif call.data == 'find_us':
        # bot.send_message(call.message.chat.id, "Наш адрес: ул. Примерная, д. 1")
        bot.send_message(call.message.chat.id,
                         "Наш адрес: Самара, пр.Кирова 419Б (https://vk.com/bufet_shtopor?w=address-229652500_86163)")

    elif call.data == 'menu':
        with open('doc/menu1.txt', 'r', encoding='utf-8') as file:
            menu_text = f'<code>{file.read()}</code>'
        bot.send_message(call.message.chat.id, menu_text, parse_mode='HTML')
    elif call.data == 'fact':
        send_random_fact(call.message.chat.id)
    elif call.data == 'photo_gallery':
        # Отправка изображений
        photo_paths = ['doc/photo1.jpg', 'doc/photo2.jpg', 'doc/photo3.jpg', 'doc/photo4.jpg', 'doc/photo5.jpg']
        message_ids = []
        for photo_path in photo_paths:
            with open(photo_path, 'rb') as photo:
                message = bot.send_photo(call.message.chat.id, photo)
                message_ids.append(message.message_id)
                time.sleep(3)  # Пауза перед отправкой следующей фотографии

        # Удаление всех отправленных фотографий
        for message_id in message_ids:
            bot.delete_message(call.message.chat.id, message_id)
    elif call.data == 'send_message':
        # Запрос данных у пользователя
        bot.send_message(call.message.chat.id, "Пожалуйста, введите ваше имя, телефон и Ваше сообщение в формате:\nИмя: <Ваше имя>\nТелефон: <Ваш телефон>\nСообщение: <Ваше сообщение>")
        bot.register_next_step_handler(call.message, process_contact_info)

def process_contact_info(message):
    # Обработка введенной информации
    try:
        lines = message.text.split('\n')
        name = lines[0].split(': ')[1]
        phone = lines[1].split(': ')[1]
        mes = lines[2].split(': ')[1]

        # Отправка сообщения с контактной информацией
        bot.send_message(message.chat.id, f"Спасибо, {name}! Ваши данные получены:\nТелефон: {phone}\nСообщение: {mes}")

        # Здесь можно добавить код для сохранения данных или отправки их администратору

    except IndexError:
        bot.send_message(message.chat.id, "Ошибка в формате ввода. Пожалуйста, следуйте указанному формату:\nИмя: <Ваше имя>\nТелефон: <Ваш телефон>\nСообщение: <Ваше сообщение>")

@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/fact - Показать случайный факт\n"
        "/working_hours - Режим работы\n"
        "/find_us - Как нас найти\n"
        "/menu - Меню\n"
        "Бла-бла-бла................................"
    )
    bot.send_message(message.chat.id, help_text)

if __name__ == '__main__':
    print('Бот включен!')
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print('Бот выключен пользователем!')
    except Exception as e:
        print(f'Неожиданная ошибка: {e}')
    finally:
        print('Завершение работы бота...')
