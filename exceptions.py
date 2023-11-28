class StatusCodeException(Exception):
    """Получен HTTP response code отличный от 200."""


class StatusError(Exception):
    """Несоответсвие (отсутствие) ключей в ответе API и в документации."""


class EmptyResponceError(Exception):
    """Вызывается если отсутствует ключ homeworks в ответе."""


class SendingError(Exception):
    """Вызывается при условие ошибки отправки сообщений."""


class ResponceKeyError(Exception):
    """Возникает при несоответствии ключа словоря в ответе API."""


class ValueTokensError(Exception):
    """Возникаает при отсутствие одного из токенов."""
