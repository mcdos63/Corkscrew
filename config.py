# config.py

# Пути к файлам
PATH = 'doc/'
BOT_FILE_PATH = 'doc/bot.txt'
FACTS_FILE_PATH = 'doc/facts.txt'
MENU_FILE_PATH = 'doc/menu1.txt'
LOGO_PATH = 'doc/s.png'
LOG_FILE = 'doc/sent_messages.log'  # Файл для логирования отправленных сообщений
AUDIO_PATH = 'doc/audio.ogg'  # Путь для сохранения аудиофайла
GAME_URL = 'https://pi.mcdos.keenetic.link'

# Логирование и пользователи
ALLOWED_USERS = [524849386, 123456789]  # реальные user_id

# Русские названия дней недели
DAYS_OF_WEEK_RU = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье"
}

# Время работы буфета
TIME_OPEN = 12
TIME_CLOSE = 1

# Координаты для погоды
latitude = 53.259035
longitude = 50.217374

# Ваш API-ключ от OpenWeatherMap
API_KEY = '9ec75c7ee009a4ac9f254361c2289bb0'

# Фотографии для галереи
photo_paths = [
    'doc/photo1.jpg',
    'doc/photo2.jpg',
    'doc/photo3.jpg',
    'doc/photo4.jpg',
    'doc/photo5.jpg'
]