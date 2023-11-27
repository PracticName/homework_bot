class StatusCodeException(Exception):
    """Получен HTTP response code отличный от 200."""


class KeyException(Exception):
    """Несоответсвие (отсутствие) ключей в ответе API и в документации."""


class EmptyResponceError(Exception):
    """
    Вызывается если временная метка больше.
    чем время отправки последней домашней работы на ревью.
    """


class SendingError(Exception):
    """Вызывается при условие ошибки отправки сообщений."""


class ResponceKeyError(Exception):
    """Возникает при несоответствии ключа словоря в ответе API."""


class ValueTokensError(Exception):
    """Возникаает при отсутствие одного из токенов."""
