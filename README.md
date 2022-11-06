# homework_bot
python telegram bot

Telegram-бот для отслеживания статуса проверки вашей домашней работы на 
Яндекс.Практикум. Когда ревьюер проверяет вашу домашнюю работу, он присваивает 
ей один из статусов:
•	работа принята на проверку,
•	работа возвращена для исправления ошибок,
•	работа принята.
Если работа уже отправлена, но ревьюер пока не взял её на проверку, то это 
значит, что никакого статуса ей ещё не присвоено.

Бот должен:
•	раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус 
отправленной на ревью домашней работы;
•	при обновлении статуса анализировать ответ API и отправлять вам 
соответствующее уведомление в Telegram;
•	логировать свою работу и сообщать вам о важных проблемах сообщением в 
Telegram.


# Технологии (на Windows):
Python 3.7.9
python-dotenv 0.19.0
python-telegram-bot 13.7

# Чтобы запустить проект клонируем репозиторий:
git clone https://github.com/Karina-Rin/homework_bot.git

# Открываем репозиторий через командную строку:
cd homework_bot

# или через комбинацию горячих клавиш:
Ctrl+A + Ctrl+O (открываем папку с директорием: .../Dev/homework_bot)

# Cоздаем и активировуем виртуальное окружение:
python -m venv venv
source venv/Scripts/activate

# Установливаем зависимости:
pip install -r requirements.txt

# Записываем в переменные окружения (файл .env) необходимые ключи:
PRACTICUM_TOKEN
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID

# Запускаем проект:
CTRL + SHIFT + D + F5
