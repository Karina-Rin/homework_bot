"""Это телеграм-бот для проверки статуса работы."""

import json
import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщения в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError:
        logger.error("Сбой при отправке сообщения в Telegram")
        raise Exception("Сбой при отправке сообщения в Telegram")
    else:
        logger.info("Сообщение отправлено в Telegram")


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API-сервиса."""
    logger.info("Направляю запрос о статусе домашки")
    params = {"from_date": current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                logger.error("ENDPOINT недоступен")
                raise Exception("ENDPOINT недоступен")
            else:
                logging.error("Сбой при запросе к ENDPOINT")
                raise Exception("Сбой при запросе к ENDPOINT")
    except requests.exceptions.RequestException:
        logger.error("URL недоступен")
        raise Exception("URL недоступен")
    try:
        response = response.json()
    except json.decoder.JSONDecodeError:
        logger.error("С сервера приходит ответ не в формате json")
        raise Exception("С сервера приходит ответ не в формате json")
    logger.info("Запрос прошел успешно")
    return response


def check_response(response):
    """Проверка ответа API на корректность."""
    logger.info("Проверяю ответ API на корректность")
    if type(response) is dict:
        if "current_date" in response and "homeworks" in response:
            if type(response.get("homeworks")) is list:
                logger.info("Ответ от сервера получен")
                if response.get("homeworks"):
                    return [
                        response.get("homeworks")[0],
                        response.get("current_date"),
                    ]
                else:
                    logger.info("Отсутствуют домашние работы для проверки")
                    raise Exception("Отсутствуют домашние работы для проверки")
            else:
                logger.error("Неверный тип данных ключа homeworks")
                raise TypeError("Неверный тип данных ключа homeworks")
        else:
            logger.error("Отсутствуют ожидаемые ключи в ответе API")
            raise KeyError("Отсутствуют ожидаемые ключи в ответе API")
    else:
        logger.error("Поступил неверный тип данных")
        raise TypeError("Поступил неверный тип данных")


def parse_status(homework):
    """Извлечение из информации о домашней работе статуса работы."""
    logger.info("Извлекаю статус домашней работы")
    if "homework_name" in homework and "status" in homework:
        homework_name = homework.get("homework_name")
        homework_status = homework.get("status")
        if homework_status in HOMEWORK_STATUSES:
            verdict = HOMEWORK_STATUSES[homework_status]
            logger.info("Извлечение прошло успешно")
            return (
                f'Изменился статус проверки работы "{homework_name}".'
                f"{verdict}"
            )
        else:
            logger.error("Статус домашней работы не определен")
            raise KeyError("Статус домашней работы не определен")
    else:
        logger.error("Статус отсутствует")
        raise KeyError("Статус отсутствует")


def check_tokens():
    """Отправка сообщения в Telegram чат."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    previous_message = ""

    while True:
        try:
            if check_tokens():
                response = get_api_answer(current_timestamp)
                homework = check_response(response)[0]
                current_timestamp = check_response(response)[1]
                message = parse_status(homework)
            else:
                raise Exception("Ошибка при получении токенов")
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            current_timestamp = int(time.time() - RETRY_TIME)
        finally:
            if message != previous_message:
                send_message(bot, message)
            else:
                logger.debug("Новые статусы отсутствуют")
            previous_message = message
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
