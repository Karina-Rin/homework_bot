"""Это телеграмм-бот для проверки статуса работы."""

import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (
    ApiError,
    NameNotFound,
    ResponseKeysError,
    ResponseTypeError,
    StatusNotFound,
    TelegramError,
    TypeError,
)

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


def send_message(bot, message):
    """Отправка сообщения в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError:
        logger.error("Сбой при отправке сообщения в Telegram")
        raise TelegramError
    else:
        logger.info("Сообщение отправлено в Telegram")


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API-сервиса."""
    params = {"from_date": current_timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
    except Exception as error:
        logging.error(f"Сбой при запросе к ENDPOINT: {error}")
        raise Exception(f"Сбой при запросе к ENDPOINT: {error}")
    if homework_statuses.status_code != HTTPStatus.OK:
        status_code = homework_statuses.status_code
        logging.error(f"Ошибка {status_code}")
        raise ApiError(f"Ошибка {status_code}")
    try:
        return homework_statuses.json()
    except ValueError:
        logger.error("С сервера приходит ответ не в формате json")
        raise ApiError


def check_response(response):
    """Проверка ответа API на корректность."""
    if type(response) is not dict:
        raise ResponseTypeError
    try:
        homeworks_list = response["homeworks"]
    except KeyError:
        logger.error("Отсутствуют ожидаемые ключи в ответе API")
        raise ResponseKeysError
    try:
        homework = homeworks_list[0]
    except IndexError:
        logger.error("Отсутствуют домашние работы для проверки")
        raise TypeError
    return homework


def parse_status(homework):
    """Извлечение из информации о домашней работе статуса работы."""
    if "homework_name" in homework and "status" in homework:
        homework_name = homework.get("homework_name")
        homework_status = homework.get("status")
        if homework_status in HOMEWORK_STATUSES:
            verdict = HOMEWORK_STATUSES[homework_status]
            return (
                f'Изменился статус проверки работы "{homework_name}".'
                f"{verdict}"
            )
        else:
            logger.error("Статус домашней работы не определен")
            raise NameNotFound
    else:
        raise StatusNotFound


def check_tokens():
    """Отправка сообщения в Telegram чат."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical("Один из токенов недоступен. Завершение работы.")
        sys.exit(0)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_message = ""
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                if last_message != message:
                    send_message(bot, message)
                    last_message = message
            else:
                logger.debug("Новые статусы отсутствуют")
            current_timestamp = int(time.time())
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logger.error(message)
            if last_message != message:
                send_message(bot, message)
                last_message = message
        else:
            logger.debug("Отправка повторного запроса")
        finally:
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - '%(funcName)s'\
            - '%(lineno)d')"
    )
    handler.setFormatter(formatter)
    main()
