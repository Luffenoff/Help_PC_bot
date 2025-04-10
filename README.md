# PC Helper Bot

Телеграм-бот для помощи в подборе компьютерных комплектующих и готовых сборок.

## Особенности

- Подбор комплектующих по категориям и бюджету
- Просмотр готовых сборок ПК
- База данных с информацией о компонентах и ценах
- Удобный интерфейс взаимодействия через Telegram

## Установка и запуск

1. Клонируйте репозиторий:
```
git clone https://github.com/yourusername/pc-helper-bot.git
cd pc-helper-bot
```

2. Создайте виртуальное окружение и установите зависимости:
```
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта и добавьте токен бота:
```
BOT_TOKEN=your_telegram_bot_token
```

4. Запустите бота:
```
python bot.py
```

## Структура проекта

- `bot.py` - Основной файл бота
- `pc_helper.db` - База данных SQLite с информацией о компонентах и сборках
- `requirements.txt` - Зависимости проекта

## Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку по использованию бота

## Технологии

- Python 3.8+
- python-telegram-bot
- SQLite
- Pandas

## Лицензия

MIT