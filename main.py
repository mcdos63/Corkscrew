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
log_file = 'doc/sent_messages.log'  # Файл для логирования отправленных сообщений

text1 = '''Буфет работает в ночное время, что делает его удобным местом для приобретения напитков после закрытия основных магазинов. Заведение предлагает как напитки, так и сопутствующие закуски, что позволяет посетителям получить всё необходимое в одном месте.
Важно отметить, что заведение открыто для посетителей и готово предложить свои услуги в удобное для Вас время. ⌚'''

# Чтение токена бота из файла
bot_id = open(bot_file_path, 'r', encoding='utf-8').read().strip()
bot = telebot.TeleBot(bot_id)

# Логирование и пользователи
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
allowed_users = [524849386, 123456789]  # реальные user_id
user_states = {}

# Русские названия дней недели
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


def get_current_time():
    now = datetime.now()
    day_of_week = days_of_week_ru[now.strftime("%A")]
    current_time = now.strftime("%H:%M")
    current_hour = int(current_time.split(':')[0])
    return now, day_of_week, current_time, current_hour

# Команда /upload
@bot.message_handler(commands=['upload'])
def upload_command(message):
    if message.from_user.id not in allowed_users:
        bot.reply_to(message, "У вас нет прав для загрузки файлов.")
        return
    user_states[message.from_user.id] = "awaiting_file"
    bot.reply_to(message, "Отправьте файл для загрузки.")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    if user_states.get(user_id) != "awaiting_file":
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = f"{PATH}/{message.document.file_name}"

    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    logging.info(f"User {user_id} uploaded file: {message.document.file_name}")
    user_states.pop(user_id, None)
    bot.reply_to(message, "Файл успешно загружен.")

# Логирование отправленных сообщений
def log_sent_message(user_id, first_name, last_name, username, text):
    with open(log_file, 'a', encoding='utf-8') as f:
        log_entry = {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name or "Не указана",
            'username': username or "Не указан",
            'text': text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        f.write(f"{log_entry}\n")


# # Обработка отправки сообщений администратору
# @bot.message_handler(commands=['send_message'])
# def send_message_command(message):
#     bot.send_message(message.chat.id, "Введите ваше сообщение:")
#     bot.register_next_step_handler(message, process_user_message)


def process_user_message(message):
    try:
        user_info = f'''ID: {message.from_user.id}
Имя: {message.from_user.first_name}
Фамилия: {message.from_user.last_name or ""}
Username: @{message.from_user.username or ""}
Сообщение: {message.text}'''

        # Логируем сообщение
        log_sent_message(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
            message.text
        )
        logging.info(f"User {message.from_user.id}:{message.from_user.first_name} Username:@{message.from_user.username or ''} send message: {message.text}")
        # Отправляем сообщение администратору
        admin_id = allowed_users[0]
        bot.send_message(admin_id, user_info)
        bot.send_message(message.chat.id, f"{message.from_user.first_name}, ваше сообщение отправлено администратору.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при отправке сообщения: {e}")


# Команда для просмотра логов администраторами
@bot.message_handler(commands=['logs'])
def show_logs(message):
    if message.from_user.id not in allowed_users:
        bot.reply_to(message, "У вас нет прав для просмотра логов.")
        return

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()[-10:]  # Последние 10 записей
        response = "Последние 10 отправленных сообщений:\n"
        for entry in logs:
            data = eval(entry.strip())
            response += (
                f"От: {data['first_name']} {data['last_name'] or ''} (@{data['username']})\n"
                f"Время: {data['timestamp']}\n"
                f"Текст: {data['text']}\n---\n"
            )
        bot.send_message(message.chat.id, response)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Логи сообщений отсутствуют.")


# Функция создания inline-клавиатуры
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


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    now, day_of_week, current_time, current_hour = get_current_time()
    status = ('Двери буфета открыты...'
              if (time_open <= current_hour < 24) or (0 <= current_hour < time_close)
              else 'Двери буфета пока закрыты...')

    start_text = (
        f'<b>Сегодня прекрасный день! {day_of_week}, время {current_time}.</b>\n'
        f'{status}\n'
        f"В буфете <b>\"Штопор\"</b> вы можете насладиться разнообразными закусками и напитками.\n"
        f"<i>У нас приятный интерьер, доброжелательные сотрудники и большое разнообразие блюд для всех возрастов!</i>\n"
    )

    sti = open(logo, 'rb')
    bot.send_sticker(message.chat.id, sti, message_effect_id='5046509860389126442')
    bot.send_message(message.chat.id, f'🎉 Добро пожаловать, {message.from_user.first_name}! 🎉', parse_mode='HTML')
    bot.send_message(message.chat.id, start_text, parse_mode='HTML')
    markup = create_inline_keyboard()
    bot.send_message(message.chat.id, "✨ Выберите опцию: ✨", reply_markup=markup)


# Общая функция для обработки команд и inline-кнопок
def handle_action(action, chat_id):
    if action == 'working_hours':
        bot.send_message(chat_id, text=f"{text1}\n\n⏰ Режим работы: {time_open}:00 - {time_close:02}:00",
                         parse_mode='HTML', message_effect_id='5046509860389126442')

    elif action == 'contacts':
        bot.send_message(chat_id, text='''🏪 Буфет "Штопор" находится по адресу:
📍 Проспект Кирова 419Б, Самара.
📞 Телефон для связи: +7 (917)8192194''', parse_mode='HTML')
        bot.send_location(chat_id, latitude=53.259035, longitude=50.217374)

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
                bot.send_message(chat_id, f'💡 Интересный факт: {random_fact}',
                                 message_effect_id='5046509860389126442')
        except Exception as e:
            bot.send_message(chat_id, f"❌ Ошибка при чтении фактов: {e}")

    elif action == 'photos':
        photo_paths = ['doc/photo1.jpg', 'doc/photo2.jpg', 'doc/photo3.jpg', 'doc/photo4.jpg', 'doc/photo5.jpg']
        sent_messages = []

        for photo_path in photo_paths:
            try:
                with open(photo_path, 'rb') as photo:
                    msg = bot.send_photo(chat_id, photo)
                    sent_messages.append(msg.message_id)
                    time.sleep(1)
            except Exception as e:
                bot.send_message(chat_id, f"❌ Ошибка при отправке фото: {e}")
                break

        # Удаление фотографий после просмотра
        time.sleep(10)  # Даём время на просмотр
        for msg_id in sent_messages:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                bot.send_message(chat_id, f"❌ Ошибка при удалении фото: {e}")

    elif action == 'send_message':
        bot.send_message(chat_id, "Введите ваше сообщение:")
        bot.register_next_step_handler_by_chat_id(chat_id, process_user_message)


# Обработка inline-кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    handle_action(call.data, call.message.chat.id)


# Обработка текстовых команд
@bot.message_handler(commands=['working_hours', 'contacts', 'menu', 'fact', 'photos', 'send_message'])
def command_handler(message):
    action = message.text.lstrip('/').lower()  # Убираем слэш и преобразуем в lowercase
    handle_action(action, message.chat.id)


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
    print('🤖 Бот включен!')
    while True:
        try:
            bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print('🛑 Бот выключен пользователем!')
            break
        except Exception as e:
            print(f'⚠️ Неожиданная ошибка: {e}')
            time.sleep(5)  # Перезапуск через 5 секунд
    print('🏁 Завершение работы бота...')