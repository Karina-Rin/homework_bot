"""Ошибки для homework."""


class TelegramError(Exception):
    """Сбой при отправке сообщения в Telegram."""

    pass


class ApiError(Exception):
    """С сервера приходит ответ не в формате json."""

    pass


class ResponseTypeError(TypeError):
    """Тип данных ответа от API адреса не dict."""

    pass


class ResponseKeysError(KeyError):
    """Отсутствуют ожидаемые ключи в ответе API."""

    pass


class TypeError(TypeError):
    """Отсутствуют домашние работы для проверки."""

    pass


class NameNotFound(KeyError):
    """Статус домашней работы не определен."""

    pass


class StatusNotFound(KeyError):
    """Статус отсутствует."""

    pass
