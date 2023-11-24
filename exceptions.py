class StatusCodeException(Exception):
    """Получен HTTP response code отличный от 200."""

    def __init__(self, text):
        """Инициализация."""
        self.text = text


class KeyException(Exception):
    """Несоответсвие (отсутствие) ключей в ответе API и в документации."""

    def __init__(self, text):
        """Инициализация."""
        self.text = text


class TimestampException(Exception):
    """
    Вызывается если временная метка больше.
    чем время отправки последней домашней работы на ревью.
    """

    def __init__(self, text):
        """Инициализация."""
        self.text = text


class SendingError(Exception):
    """Вызывается при условие ошибки отправки сообщений."""

    pass
