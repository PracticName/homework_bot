class StatusCodeException(Exception):
    """Исключение которое вызывается при ответе сервера отличного от 200."""

    def __init__(self, text):
        """Инициализация."""
        self.text = text


class VerdictException(Exception):
    """Исключение извлечения переменной из 'HOMEWORK_VERDICTS'."""

    def __init__(self, text):
        """Инициализация."""
        self.text = text


class KeyException(Exception):
    """Осутствует ключ."""

    def __init__(self, text):
        """Инициализация."""
        self.text = text
