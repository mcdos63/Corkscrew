import telebot
import time
import random
import logging
from datetime import datetime
from telebot import types

# Пути к файлам
PATH = 'doc/'
bot_file_path = 'doc/bot.txt'
facts_file_path = 'doc/facts.txt'
menu_file_path = 'doc/menu1.txt'
logo = 'doc/s.png'


# Читаем файл и исключаем пустые строки
def read_file(file_path) -> list[str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            return [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"Произошла ошибка при чтении файла: {e}")
            return []


# Чтение токена бота из файла
bot_id = read_file(bot_file_path)[0]
bot = telebot.TeleBot(bot_id)

# Логирование для отслеживания загрузок
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Список разрешенных пользователей
allowed_users = [123456789, 524849386]  # реальные user_id
user_states = {}


# Функция для получения текущего времени
def get_current_time():
    now = datetime.now()
    day_of_week = days_of_week_ru[now.strftime("%A")]
    current_time = now.strftime("%H:%M")
    current_hour = int(current_time.split(':')[0])
    return now, day_of_week, current_time, current_hour


days_of_week_ru = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье"
}

time_open = 12
time_close = 1


# Создание inline-клавиатуры
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("Режим работы", callback_data="working_hours"),
        types.InlineKeyboardButton("Наши контакты", callback_data="contacts"),
        types.InlineKeyboardButton("Меню", callback_data="menu"),
        types.InlineKeyboardButton("Интересные факты", callback_data="fact"),
        types.InlineKeyboardButton("Фотогалерея", callback_data="photos"),
        types.InlineKeyboardButton("Отправить сообщение", callback_data="send_message")
    ]
    markup.add(*buttons)
    return markup


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        now, day_of_week, current_time, current_hour = get_current_time()

        status = ('Двери буфета открыты...'
                  if (time_open <= current_hour < 24) or (0 <= current_hour < time_close)
                  else 'Двери буфета пока закрыты...')

        start_text = (
            f'<b>Сегодня прекрасный день! {day_of_week}, время {current_time}.</b>\n'
            f'{status}\n'
            f"В буфете <b>\"Штопор\"</b> вы можете насладиться разнообразными закусками и напитками на любой вкус.\n"
            f"<i>У нас приятный интерьер, доброжелательные сотрудники и большое разнообразие блюд для всех возрастов!</i>\n"
        )

        sti = open(logo, 'rb')
        bot.send_sticker(message.chat.id, sti, message_effect_id='5046509860389126442')
        bot.send_message(message.chat.id, f'🎉 Добро пожаловать, {message.from_user.first_name}! 🎉', parse_mode='HTML')
        bot.send_message(message.chat.id, start_text, parse_mode='HTML')
        markup = create_inline_keyboard()
        bot.send_message(message.chat.id, "✨ Выберите опцию: ✨", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


# Общая функция для обработки действий
def handle_action(action, message_or_call):
    chat_id = message_or_call.message.chat.id if hasattr(message_or_call, 'message') else message_or_call.chat.id

    if action == 'working_hours':
        bot.send_message(chat_id, text=f"⏰ Режим работы: {time_open}:00 - {time_close:02}:00", parse_mode='HTML')

    elif action == 'contacts':
        bot.send_message(chat_id, text='''🏪 Буфет "Штопор" находится по адресу:
📍 Проспект Кирова 419Б, Самара.
📞 Телефон для связи: +7 (917)8192194''', parse_mode='HTML')
        bot.send_location(chat_id, latitude=53.259035, longitude=50.217374)  # Пример координат

    elif action == 'menu':
        try:
            with open(menu_file_path, 'r', encoding='utf-8') as file:
                menu_text = f'<code>{file.read()}</code>'
            bot.send_message(chat_id, menu_text, parse_mode='HTML')
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ошибка при чтении меню: {e}")

    elif action == 'fact':
        try:
            with open(facts_file_path, 'r', encoding='utf-8') as file:
                lines = file.read().splitlines()
                if not lines:
                    bot.send_message(chat_id, "🧐 Факты временно недоступны.")
                    return
                random_fact = random.choice(lines)
                bot.send_message(chat_id, f'💡 Интересный факт: {random_fact}')
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ошибка при чтении фактов: {e}")

    elif action == 'photos':
        photo_paths = ['doc/photo1.jpg', 'doc/photo2.jpg', 'doc/photo3.jpg', 'doc/photo4.jpg', 'doc/photo5.jpg']
        for photo_path in photo_paths:
            try:
                with open(photo_path, 'rb') as photo:
                    bot.send_photo(chat_id, photo)
                    time.sleep(1)  # Пауза между фото
            except Exception as e:
                bot.send_message(chat_id, f"❌ Ошибка при отправке фото: {e}")
                break

    elif action == 'send_message':
        bot.send_message(chat_id, "📝 Пожалуйста, введите ваше имя, телефон и сообщение в формате:\n"
                                  "Имя: <Ваше имя>\n"
                                  "Телефон: <Ваш телефон>\n"
                                  "Сообщение: <Ваше сообщение>")
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
    action = message.text.lstrip('/').lower()
    handle_action(action, message)


# Обработка контактной информации
def process_contact_info(message):
    try:
        data = {}
        lines = message.text.split('\n')
        for line in lines:
            key, value = line.split(': ', 1)
            data[key.strip()] = value.strip()
        name = data.get('Имя')
        phone = data.get('Телефон')
        mes = data.get('Сообщение')
        if not all([name, phone, mes]):
            raise ValueError("Недостаточно данных.")
        bot.send_message(message.chat.id, f"✅ Спасибо, {name}! Ваши данные получены:\n"
                                          f"📞 Телефон: {phone}\n"
                                          f"💬 Сообщение: {mes}")
    except ValueError as ve:
        bot.send_message(message.chat.id, f"❌ Ошибка: {ve}. Пожалуйста, следуйте указанному формату.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {e}")


# Команда /help
@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = (
        "📚 Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/working_hours - Режим работы\n"
        "/contacts - Наши контакты\n"
        "/menu - Меню\n"
        "/fact - Показать случайный факт\n"
        "/photos - Фотогалерея\n"
        "/send_message - Отправить сообщение администратору"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


if __name__ == '__main__':
    print('🤖 Бот включен!')
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print('🛑 Бот выключен пользователем!')
    except Exception as e:
        print(f'⚠️ Неожиданная ошибка: {e}')
    finally:
        print('🏁 Завершение работы бота...')