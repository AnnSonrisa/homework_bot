## Проект: Telegram-бот

Учебный проект: "Telegram-бот", который будет обращаться к API сервиса Практикум.Домашка и узнавать статус домашней работы.  
В рамках курса __Backend-developer__ на платформе __Яндекс.Практикум__.


# Как запустить проект:

1) Клонировать репозиторий и перейти в него в командной строке:
git clone https://github.com/AnnSonrisa/homework_bot.git

2) Cоздать и активировать виртуальное окружение:
python -m venv venv

source venv/Scripts/activate

3) Установить зависимости из файла requirements.txt:
python -m pip install --upgrade pip

pip install -r requirements.txt

4) Создайте и заполните файл .env:

touch .env


PRAKTIKUM_TOKEN= ...   /* your Yandex.Practicum Homrwork API token */
TELEGRAM_TOKEN= ...    /* your Telegram bot token */
TELEGRAM_CHAT_ID= ...  /* yout Telegram chat id */


5) Запустите homework.py:

python3 homework.py
