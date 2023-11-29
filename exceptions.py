class StatusCodeException(Exception):
    """Получен HTTP response code отличный от 200."""

    pass


class StatusError(Exception):
    """Несоответсвие (отсутствие) ключей в ответе API и в документации."""

    pass


class EmptyResponceError(Exception):
    """Вызывается если отсутствует ключ homeworks в ответе."""

    pass


class SendingError(Exception):
    """Вызывается при условие ошибки отправки сообщений."""

    pass


class ResponceKeyError(Exception):
    """Возникает при несоответствии ключа словоря в ответе API."""

    pass


class ValueTokensError(Exception):
    """Возникаает при отсутствие одного из токенов."""

    pass


class RequestError(Exception):
    """Возникает при недоступности ендпоинта."""

    pass
