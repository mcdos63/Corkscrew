import telebot
import tempfile
import time
import requests
import random
import logging
from datetime import datetime
from telebot import types
from gtts import gTTS
import os

# Импорт констант и настроек из config.py
from config import (
    PATH,
    BOT_FILE_PATH,
    FACTS_FILE_PATH,
    MENU_FILE_PATH,
    LOGO_PATH,
    LOG_FILE,
    AUDIO_PATH,
    ALLOWED_USERS,
    DAYS_OF_WEEK_RU,
    TIME_OPEN,
    TIME_CLOSE,
    latitude,
    longitude,
    API_KEY,
    photo_paths
)

# Логирование и пользователи
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
user_states = {}


def get_weather(latitude=latitude, longitude=longitude):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            return "Не удалось получить данные о погоде. Пожалуйста, попробуйте позже."

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        city_name = data["name"]

        weather_info = {
            "город": city_name,
            "температура": f"{temp}°C",
            "ощущается_как": f"{feels_like}°C",
            "влажность": f"{humidity}%",
            "скорость_ветра": f"{wind_speed} м/с",
            "описание": weather
        }
        return weather_info

    except Exception as e:
        logging.error(f"Ошибка при получении данных о погоде: {e}")
        return "Не удалось получить данные о погоде. Пожалуйста, попробуйте позже."


# Чтение токена бота из файла
try:
    with open(BOT_FILE_PATH, 'r', encoding='utf-8') as file:
        BOT_TOKEN = file.read().strip()
except FileNotFoundError:
    logging.error("Файл с токеном бота не найден.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)


# Получение текущего времени
def get_current_time():
    now = datetime.now()
    day_of_week = DAYS_OF_WEEK_RU[now.strftime("%A")]
    current_time = now.strftime("%H:%M")
    current_hour = int(current_time.split(':')[0])
    return now, day_of_week, current_time, current_hour


def text_to_speech_and_send(chat_id, text):
    try:
        # Преобразование текста в речь
        tts = gTTS(text=text, lang='ru')
        tts.save(AUDIO_PATH)
        # Отправка аудиофайла пользователю
        with open(AUDIO_PATH, 'rb') as audio:
            sent_message = bot.send_voice(chat_id, audio)  # Сохраняем отправленное сообщение
        # Удаление временного аудиофайла
        os.remove(AUDIO_PATH)
        # Удаление сообщения через 10 секунд
        time.sleep(10)
        bot.delete_message(chat_id, sent_message.message_id)  # Используем message_id отправленного сообщения
    except Exception as e:
        logging.error(f"Ошибка при преобразовании текста в речь: {e}")
        bot.send_message(chat_id, "Произошла ошибка при преобразовании текста в речь. Попробуйте снова.")


# Текст приветствия
def start_text():
    _, day_of_week, current_time, current_hour = get_current_time()
    status = (
        'Двери буфета открыты...'
        if (TIME_OPEN <= current_hour < 24) or (0 <= current_hour < TIME_CLOSE)
        else 'Двери буфета пока закрыты...')
    weather = get_weather()
    return (
        f'<b>Сегодня прекрасный день! {day_of_week} {weather.get('температура', '')}, время {current_time}.</b>\n'
        f'{status}\n'
        f"В буфете <b>\"Штопор\"</b> вы можете насладиться разнообразными закусками и напитками.")


# Логирование отправленных сообщений
def log_sent_message(user_id, first_name, phone, text):
    log_entry = {
        'user_id': user_id,
        'first_name': first_name,
        'phone': phone or "Не указан",
        'text': text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{log_entry}\n")
    except Exception as e:
        logging.error(f"Ошибка при записи лога: {e}")


# Проверка прав администратора
def is_admin(message):
    return message.from_user.id in ALLOWED_USERS


# Создание inline-клавиатуры
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("Режим работы", callback_data="working_hours"),
        types.InlineKeyboardButton("Наши контакты", callback_data="contacts"),
        types.InlineKeyboardButton("Меню", callback_data="menu"),
        types.InlineKeyboardButton("Интересные факты", callback_data="fact"),
        types.InlineKeyboardButton("Фотогалерея", callback_data="photos"),
        types.InlineKeyboardButton("Отправить сообщение", callback_data="letter"),
        types.InlineKeyboardButton("Проговорить текст", callback_data="speak")
    ]
    markup.add(*buttons)
    return markup


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        with open(LOGO_PATH, 'rb') as logo:
            bot.send_sticker(message.chat.id, logo, message_effect_id='5046509860389126442')
    except FileNotFoundError:
        logging.error("Логотип не найден.")

    bot.send_message(message.chat.id, f'🎉 Добро пожаловать, {message.from_user.first_name}! 🎉', parse_mode='HTML')
    bot.send_message(message.chat.id, start_text(), parse_mode='HTML')
    markup = create_inline_keyboard()
    bot.send_message(message.chat.id, "✨ Выберите опцию: ✨", reply_markup=markup)
    # print(get_weather(latitude, longitude))


# Запрос контакта
def process_contact(call):
    user_id = call.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_contact = types.KeyboardButton("Поделиться контактом", request_contact=True)
    markup.add(button_contact)

    # Отправляем сообщение с кнопкой для поделиться контактом
    sent_message = bot.send_message(
        call.message.chat.id,
        "Пожалуйста, поделитесь своим контактом:",
        reply_markup=markup
    )
    user_states[user_id] = {"message_id": sent_message.message_id, "state": "awaiting_contact"}


# Обработка контакта
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id)
    if not user_state or user_state.get("state") != "awaiting_contact":
        return
    phone_number = message.contact.phone_number if message.contact else None
    user_states[user_id] = {"phone": phone_number, "state": "awaiting_message"}
    try:
        # Отправляем новое сообщение вместо редактирования старого
        bot.send_message(
            message.chat.id,
            "Контакт получен. Теперь введите ваше сообщение:"
        )
        # Скрываем клавиатуру и запрашиваем текст сообщения
        bot.send_message(
            message.chat.id,
            "Введите ваше сообщение:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, process_user_message_with_contact)

    except Exception as e:
        logging.error(f"Неожиданная ошибка: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла неожиданная ошибка. Попробуйте снова."
        )


# Обработка текстового сообщения после получения контакта
def process_user_message_with_contact(message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id)

    if not user_state or user_state.get("state") != "awaiting_message":
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте снова.")
        return

    phone_number = user_state.get("phone")
    try:
        # Логируем сообщение
        log_sent_message(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            phone=phone_number,
            text=message.text
        )

        # Отправляем сообщение администратору
        admin_id = ALLOWED_USERS[0]
        user_info = (
            f"ID: {message.from_user.id}\n"
            f"Имя: {message.from_user.first_name}\n"
            f"Телефон: {phone_number or 'Не указан'}\n"
            f"Сообщение: {message.text}"
        )
        bot.send_message(admin_id, user_info)
        bot.send_message(message.chat.id, f"{message.from_user.first_name}, ваше сообщение отправлено администратору.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при отправке сообщения: {e}")

    finally:
        # Очищаем состояние пользователя
        user_states.pop(user_id, None)


# Команда /logs
@bot.message_handler(commands=['logs'])
def show_logs(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ У вас нет прав для просмотра логов.")
        return
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = f.readlines()[-10:]  # Последние 10 записей
        response = "Последние 10 отправленных сообщений:\n"
        for entry in logs:
            data = eval(entry.strip())  # Безопасный парсинг JSON
            response += (
                f"От: {data['first_name']}\n"
                f"Телефон: {data['phone']}\n"
                f"Время: {data['timestamp']}\n"
                f"Текст: {data['text']}\n---\n"
            )
        bot.send_message(message.chat.id, response)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "❌ Логи сообщений отсутствуют.")


# Команда /upload
@bot.message_handler(commands=['upload'])
def upload_command(message):
    if is_admin(message):
        user_states[message.from_user.id] = "awaiting_file"
        bot.reply_to(message, "Отправьте файл для загрузки.")
    else:
        bot.reply_to(message, "У вас нет прав для загрузки файлов.")


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


# Обработка inline-кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    action = call.data
    chat_id = call.message.chat.id

    if action == 'working_hours':
        bot.send_message(chat_id, f"⏰ Режим работы: {TIME_OPEN}:00 - {TIME_CLOSE:02}:00", parse_mode='HTML',
                         message_effect_id='5046509860389126442')
    elif action == 'contacts':
        bot.send_message(chat_id, '''🏪 Буфет "Штопор" находится по адресу:
📍 Проспект Кирова 419Б, Самара.
📞 Телефон для связи: +7 (917)8192194''', parse_mode='HTML')
        bot.send_location(chat_id, latitude=latitude, longitude=longitude)
    elif action == 'menu':
        try:
            with open(MENU_FILE_PATH, 'r', encoding='utf-8') as file:
                menu_text = f'<code>{file.read()}</code>'
            bot.send_message(chat_id, menu_text, parse_mode='HTML')
        except FileNotFoundError:
            bot.send_message(chat_id, "❌ Меню временно недоступно.")
    elif action == 'fact':
        try:
            with open(FACTS_FILE_PATH, 'r', encoding='utf-8') as file:
                lines = file.read().splitlines()
                if not lines:
                    bot.send_message(chat_id, "🧐 Факты временно недоступны.")
                    return
                random_fact = random.choice(lines)
                bot.send_message(chat_id, f'💡 Интересный факт: {random_fact}', message_effect_id='5046509860389126442')
                text_to_speech_and_send(chat_id, random_fact)
        except FileNotFoundError:
            bot.send_message(chat_id, "❌ Факты временно недоступны.")
    elif action == 'photos':
        # photo_paths = ['doc/photo1.jpg', 'doc/photo2.jpg', 'doc/photo3.jpg', 'doc/photo4.jpg', 'doc/photo5.jpg']
        sent_messages = []
        for photo_path in photo_paths:
            try:
                with open(photo_path, 'rb') as photo:
                    msg = bot.send_photo(chat_id, photo)
                    sent_messages.append(msg.message_id)
                    time.sleep(1)
            except FileNotFoundError:
                bot.send_message(chat_id, f"❌ Фото {photo_path} не найдено.")
                break
        time.sleep(10)
        for msg_id in sent_messages:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                bot.send_message(chat_id, f"❌ Ошибка при удалении фото: {e}")
    elif action == 'letter':
        process_contact(call)
    # elif action == 'speak':
    #     bot.send_message(chat_id, "Пожалуйста, отправьте текст, который вы хотите услышать.")
    #     bot.register_next_step_handler(call.message, process_text_to_speech)


# Обработка текста для преобразования в речь
def process_text_to_speech(message):
    try:
        # Преобразование текста в речь
        tts = gTTS(text=message.text, lang='ru')
        tts.save(AUDIO_PATH)

        # Отправка аудиофайла пользователю
        with open(AUDIO_PATH, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)

        # Удаление временного аудиофайла
        os.remove(AUDIO_PATH)
    except Exception as e:
        logging.error(f"Ошибка при преобразовании текста в речь: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при преобразовании текста в речь. Попробуйте снова.")


# Команда /help
@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/working_hours - Расписание\n"
        "/contacts - Наши контакты\n"
        "/menu - Меню\n"
        "/fact - Показать случайный факт\n"
        "/photos - Фотогалерея\n"
        # "/speak - Проговорить текст\n"        
        "/letter - Отправить сообщение администратору"
    )
    if is_admin(message):
        help_text += (
            "\n-------------------------------\n"
            "Администратору:\n"
            "/upload - Загрузить файл\n"
            "/logs - Показать логи\n"
        )
    bot.send_message(message.chat.id, help_text)


# Запуск бота
if __name__ == '__main__':
    print('🤖 Бот включен!')
    while True:
        try:
            bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print('🛑 Бот выключен пользователем!')
            break
        except Exception as e:
            logging.error(f"⚠️ Неожиданная ошибка: {e}")
            time.sleep(5)  # Перезапуск через 5 секунд
    print('🏁 Завершение работы бота...')
