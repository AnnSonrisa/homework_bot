import logging
import os
import requests
import sys
import time
import telegram

from dotenv import load_dotenv

from exceptions import MissingKey, ResponseError, SendMessageError

load_dotenv()

API_RESPONSE_ERROR = ('Значение кода возрата "{response}" '
                      'не соответствует требуемому - "200".')

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

TOKEN_ERRORS = ['Отстутствует переменная окружения "TELEGRAM_TOKEN"',
                'Отстутствует переменная окружения "TELEGRAM_CHAT_ID"',
                'Отстутствует переменная окружения "PRACTICUM_TOKEN"']

STATUS_SUMMARY = ('Изменился статус проверки работы "{name}". '
                  '\n\n{verdict}')

STATUS_UNEXPECTED = 'Неожиданное значение ключа "status": {status}'

HW_NOT_LIST_ERR = 'Домашняя работа приходит не в виде списка.'
HW_NOT_IN_LIST = 'Домашней работы нет в списке.'

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

SUCCESSFUL_MSG_SENDING = 'Сообщение {message} успешно отправлено.'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

SEND_MESSAGE_ERROR = ('Ошибка {error} при отправке сообщения '
                      '{message} в Telegram')

logging.basicConfig(
    stream=sys.stdout,
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
logging.getLogger(__name__)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(SUCCESSFUL_MSG_SENDING.format(message=message))
    except Exception as error:
        raise SendMessageError(
            SEND_MESSAGE_ERROR.format(error=error, message=message))


def get_api_answer(current_timestamp):
    """
    Делает запрос к единственному эндпоинту API-сервиса.
    В случае успешного запроса возвращает ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise ResponseError(
            API_RESPONSE_ERROR.format(response=response.status_code))
    response = response.json()
    return response


def check_response(response):
    """Проверка ответа API на корректность."""
    if isinstance(response, dict):
        if 'homeworks' not in response:
            raise MissingKey(HW_NOT_IN_LIST)
    if not isinstance(response['homeworks'], list):
        raise TypeError(HW_NOT_LIST_ERR)
    return response['homeworks']


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе
    статус этой работы.
    """
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise ValueError(STATUS_UNEXPECTED.format(status=homework_status))
    return f'Изменился статус проверки работы "' \
           f'{homework_name}". {HOMEWORK_STATUSES[homework_status]}'


def check_tokens():
    """Проверяет доступность переменных окружения, которые
    необходимы для работы программы.
    Если отсутствует хотя бы одна переменная окружения —
    функция возвращает False, иначе — True.
    """
    tokens = [
        [TELEGRAM_TOKEN, None, TOKEN_ERRORS[0]],
        [TELEGRAM_CHAT_ID, None, TOKEN_ERRORS[1]],
        [PRACTICUM_TOKEN, None, TOKEN_ERRORS[2]]
    ]
    for token, value, error in tokens:
        if token is value:
            logging.critical(error)
            return False
    return True


def main():
    """Основная логика работы бота."""
    current_error = 'test error'
    try:
        check_tokens()
    except Exception as error:
        logging.critical(f'Не хватает переменной окружения! {error}')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            message = parse_status(check_response(response)[0])
            send_message(bot, message)
            current_timestamp = response.get(
                'current_date',
                current_timestamp
            )
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            current_error = message
            logging.error(message, exc_info=True)
            if current_error != message:
                send_message(bot, message)
            time.sleep(30)


if __name__ == '__main__':
    main()
