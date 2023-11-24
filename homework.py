import logging
import os
import sys
import time
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (KeyException, SendingError,
                        StatusCodeException, TimestampException)


load_dotenv()


PRACTICUM_TOKEN = os.getenv('P_TOKEN')
TELEGRAM_TOKEN = os.getenv('T_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('T_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

current_status = ''

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler()
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    env = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for i in env:
        if i is None:
            logging.critical(f'Отсутствует переменная окружения {i}')
            return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Удачная отправка сообщения в Telegram')
    except Exception:
        logger.error('Сообщение не отправлено')


def get_api_answer(timestamp):
    """
    Возвращает статус API сервиса.
        Параметры:
            timestamp (int): время в сек.
        Возвращаемое значение (str): статус сервиса.
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            logger.error('Получен HTTP response code отличный от 200')
            raise StatusCodeException('HTTP response code отличный от 200')
    except requests.RequestException as exc:
        logger.error(f'Недоступность ендпоинта домашней работы. {exc}')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if type(response) is dict and type(response.get('homeworks')) is list:
        if not response.get('homeworks'):
            logger.error('Массив домашней работы пуст.')
            raise TimestampException('Использована неверная метка времени')
        return response.get('homeworks')[0]
    else:
        logger.error('Неожиданный тип ключей словаря.')
        raise TypeError('Тип данных в ответе не соответствует документации')


def parse_status(homework):
    """Извлекает статус домашней работы."""
    global current_status
    if 'homework_name' in homework and 'status' in homework:
        homework_name = homework['homework_name']
        status = homework['status']
        if status not in HOMEWORK_VERDICTS:
            logger.error('Неожиданный статус домашней работы')
            raise KeyException('Неожиданный статус домашней работы')
        verdict = HOMEWORK_VERDICTS.get(status)
        if current_status == status:
            logger.debug('Отсутствие в ответе новых статусов')
            return ''
        current_status = status
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        logger.error('Отсутствие ожидаемых ключей в ответе API')
        raise KeyException('Отсутствует необходимый ключ в homework')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствует один из токенов')
        sys.exit(0)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            if message != '':
                send_message(bot, message)
            else:
                raise SendingError
        except SendingError:
            logger.error(
                'Сообщение не будет отпралено, так как статус не изменился')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
