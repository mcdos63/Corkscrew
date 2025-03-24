import telebot
import time
from datetime import datetime
import random
from telebot import types

# Чтение токена бота из файла
with open('doc/bot.txt', 'r') as file:
    bot_id = file.read().strip()  # Убираем лишние пробелы и переносы строки
bot = telebot.TeleBot(bot_id)

# Пути к файлам
facts_file_path = 'doc/facts.txt'
menu_file_path = 'doc/menu1.txt'
logo = 'doc/s.png'

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

time_open = 12
time_close = 1

# Определение статуса работы буфета
if (time_open <= current_hour < 24) or (0 <= current_hour < time_close):
    status = 'Двери буфета открыты. Ждём только вас, приходите скорее!'
else:
    status = 'Двери буфета пока закрыты, но мы готовимся принять Вас у нас в рабочее время.'

start_text = (
    f'<b>Сегодня прекрасный день! {day_of_week}, время {current_time}.</b>\n'
    f'{status}\n'
    f"В буфете <b>\"Штопор\"</b> вы можете насладиться разнообразными закусками и напитками на любой вкус.\n"
    f"<i>У нас приятный интерьер, доброжелательные сотрудники и большое разнообразие блюд для всех возрастов!</i>\n"
)

def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)  # 2 кнопки в строке

    # # Создание кнопок
    # buttons = [
    #     ("Режим работы", "working_hours"),
    #     ("Наши контакты", "contacts"),
    #     ("Меню", "menu"),
    #     ("Интересные факты", "fact"),
    #     ("Фотогалерея", "photos"),
    #     ("Отправить сообщение", "send_message")
    # ]
    #
    # for text, callback in buttons:
    #     markup.add(types.InlineKeyboardButton(text, callback_data=callback))
    btn1 = types.InlineKeyboardButton("Режим работы", callback_data="working_hours")
    btn2 = types.InlineKeyboardButton("Наши контакты", callback_data="contacts")
    btn3 = types.InlineKeyboardButton("Меню", callback_data="menu")
    btn4 = types.InlineKeyboardButton("Интересные факты", callback_data="fact")
    btn5 = types.InlineKeyboardButton("Фотогалерея", callback_data="photos")
    btn6 = types.InlineKeyboardButton("Отправить сообщение", callback_data="send_message")

    # Добавление кнопок в клавиатуру
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        sti = open(logo, 'rb')
        bot.send_sticker(message.chat.id, sti)

        bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!'.format(message.from_user))
        bot.send_message(message.chat.id, start_text, parse_mode='HTML')

        markup = create_inline_keyboard()
        bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


# Общая функция для обработки команд и callback-запросов
def handle_action(action, message_or_call):
    chat_id = message_or_call.message.chat.id if hasattr(message_or_call, 'message') else message_or_call.chat.id

    if action == 'working_hours':
        bot.send_message(chat_id, f"Наш режим работы: {time_open}:00 - {time_close:02}:00")
    elif action == 'contacts':
        bot.send_message(chat_id, "Наш адрес: Самара, пр. Кирова 419Б")
    elif action == 'menu':
        try:
            with open(menu_file_path, 'r', encoding='utf-8') as file:
                menu_text = f'<code>{file.read()}</code>'
            bot.send_message(chat_id, menu_text, parse_mode='HTML')
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка при чтении меню: {e}")
    elif action == 'fact':
        try:
            with open(facts_file_path, 'r', encoding='utf-8') as file:
                lines = file.read().splitlines()
                if not lines:
                    bot.send_message(chat_id, "Факты временно недоступны.")
                    return
                random_fact = random.choice(lines)
                bot.send_message(chat_id, f'{random_fact}')
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка при чтении фактов: {e}")
    elif action == 'photos':
        photo_paths = ['doc/photo1.jpg', 'doc/photo2.jpg', 'doc/photo3.jpg', 'doc/photo4.jpg', 'doc/photo5.jpg']
        message_ids = []
        for photo_path in photo_paths:
            try:
                with open(photo_path, 'rb') as photo:
                    msg = bot.send_photo(chat_id, photo)
                    message_ids.append(msg.message_id)
                    time.sleep(3)  # Пауза перед отправкой следующей фотографии
            except Exception as e:
                bot.send_message(chat_id, f"Ошибка при отправке фото: {e}")
                break

        # Удаление всех отправленных фотографий
        for message_id in message_ids:
            try:
                bot.delete_message(chat_id, message_id)
            except Exception as e:
                bot.send_message(chat_id, f"Ошибка при удалении фото: {e}")
    elif action == 'send_message':
        bot.send_message(chat_id, "Пожалуйста, введите ваше имя, телефон и сообщение в формате:\n"
                                  "Имя: <Ваше имя>\nТелефон: <Ваш телефон>\nСообщение: <Ваше сообщение>")
        if hasattr(message_or_call, 'message'):
            bot.register_next_step_handler(message_or_call.message, process_contact_info)
        else:
            bot.register_next_step_handler(message_or_call, process_contact_info)


# Обработка inline-кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    handle_action(call.data, call)


# Обработка текстовых команд
@bot.message_handler(commands=['working_hours', 'contacts', 'menu', 'fact', 'photos', 'send_message'])
def command_handler(message):
    action = message.text.lstrip('/').lower()  # Убираем слэш и преобразуем в lowercase
    handle_action(action, message)


# Обработка контактной информации
def process_contact_info(message):
    try:
        data = {}
        lines = message.text.split('\n')
        for line in lines:
            key, value = line.split(': ', 1)  # Разделяем по первому ': '
            data[key.strip()] = value.strip()

        name = data.get('Имя')
        phone = data.get('Телефон')
        mes = data.get('Сообщение')

        if not all([name, phone, mes]):
            raise ValueError("Недостаточно данных.")

        bot.send_message(message.chat.id, f"Спасибо, {name}! Ваши данные получены:\nТелефон: {phone}\nСообщение: {mes}")

    except ValueError as ve:
        bot.send_message(message.chat.id, f"Ошибка: {ve}. Пожалуйста, следуйте указанному формату.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")


# Команда /help
@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/working_hours - Режим работы\n"
        "/contacts - Наши контакты\n"
        "/menu - Меню\n"
        "/fact - Показать случайный факт\n"
        "/photos - Фотогалерея\n"
        "/send_message - Отправить сообщение администратору"
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