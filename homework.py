import logging
import os
import sys
import time
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv
from telegram.error import TelegramError

from exceptions import (
    EmptyResponceError, KeyException,
    ResponceKeyError,
    StatusCodeException, ValueTokensError
)


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


new_status = ''

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(lineno)d, %(funcName)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    env = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if not all(env):
        logging.critical('Отсутствует переменная окружения')
        return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logger.debug('Начало отправки сообщения в Telegram')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Удачная отправка сообщения в Telegram')
    except TelegramError as exc:
        logger.error(f'Сообщение не отправлено {exc}')


def get_api_answer(timestamp):
    """
    Возвращает статус API сервиса.
        Параметры:
            timestamp (int): время в сек.
        Возвращаемое значение (str): статус сервиса.
    """
    payload = {'from_date': timestamp}
    REQUEST_PARAMS = {
        'endpoint': ENDPOINT,
        'headers': HEADERS,
        'from_date': timestamp

    }
    try:
        logger.debug(f'Отправка запроса к API {REQUEST_PARAMS}')
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code == requests.codes.ok:
            return response.json()
        raise StatusCodeException('HTTP response code отличный от 200')
    except requests.RequestException as exc:
        logger.error(f'Недоступность ендпоинта домашней работы. {exc}')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не соответстыует типу "dict"')
    if 'homeworks' not in response:
        raise EmptyResponceError('Отсутствует ключ homeworks в ответе')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(
            'В Ответе API под ключом "homeworks" получен не тип "list"'
        )
    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' in homework and 'status' in homework:
        homework_name = homework['homework_name']
        status = homework['status']
        if status not in HOMEWORK_VERDICTS:
            raise KeyException('Неожиданный статус домашней работы')
        verdict = HOMEWORK_VERDICTS.get(status)
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        logger.error('Отсутствие ожидаемых ключей в ответе API')
        raise KeyException('Отсутствует необходимый ключ в homework')


def main():
    """Основная логика работы бота."""
    global new_status
    if not check_tokens():
        logger.critical('Отсутствует один из токенов')
        raise ValueTokensError('Отсутствует один из токенов')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    while True:
        old_status = new_status
        try:
            response = get_api_answer(timestamp)
            timestamp = response.get('current_date', timestamp)
            homeworks = check_response(response)
            if homeworks:
                new_status = parse_status(homeworks[0])
            else:
                new_status = 'Статус не обновился'
            if new_status != old_status:
                send_message(bot, new_status)
            else:
                logger.error('Отсутствие в ответе новых статусов')
        except ResponceKeyError:
            logger.error('Неожиданный тип ключей словаря.')
        except StatusCodeException:
            logger.error('Получен HTTP response code отличный от 200')
        except EmptyResponceError:
            logger.error('Массив домашней работы пуст.')
        except KeyError:
            logger.error('Неожиданный статус домашней работы')
        except TypeError as error:
            logger.error(f'Неожиданный тип получен в ответе {error}.')
        except Exception as error:
            new_status = f'Сбой в работе программы: {error}'
            logger.error(new_status)
            if new_status != old_status:
                send_message(bot, new_status)
        finally:
            time.sleep(RETRY_PERIOD)
        # Пытаюсь убрать дублирование кода отправки сообщения
        # в 131 и 148 строке, записав этот код в 152 и pytest начианет ругаться


if __name__ == '__main__':
    main()
