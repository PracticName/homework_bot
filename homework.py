import logging
import os
import sys
import time

from logging import StreamHandler

import requests
import telegram

from dotenv import load_dotenv

from exceptions import StatusCodeException


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
            print(f'Отсутствует переменная окружения {i}')
            return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(timestamp):
    """
    Возвращает статус API сервиса.
        Параметры:
            timestamp (int): время в сек.
        Возвращаемое значение (str): статус сервиса.
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, HEADERS, payload)
    except requests.RequestException as exc:
        ...
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise StatusCodeException('Получен не корректный ответ от сервера')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if type(response) is dict and type(response.get('homeworks')) is list:
        return response.get('homeworks')[0]
    else:
        raise TypeError('Ошибка данных')


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' in homework and 'status' in homework:
        homework_name = homework.get('homework_name')
        verdict = homework.get('status')
    else:
        raise KeyError('Некорректный ответ')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствует ТОКЕН')
        sys.exit(0)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    ...

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.critical(message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
