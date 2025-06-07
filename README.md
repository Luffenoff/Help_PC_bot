# Help PC Bot

Телеграм-бот для помощи в сборке компьютеров и подборе компонентов.

## Возможности

- 🖥️ Подбор готовых сборок ПК по типу и ценовой категории
- 🔧 Просмотр отдельных компонентов с характеристиками
- 🎵 Смена обоев и воспроизведение музыки на сервере
- 💡 Система предложений по улучшению бота
- ❓ Подробная справка по использованию

## Требования

- Python 3.8 или выше
- PostgreSQL
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/Help_PC_bot.git
cd Help_PC_bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории проекта:
```env
BOT_TOKEN=your_telegram_bot_token
DB_HOST=localhost
DB_PORT=5432
DB_NAME=help_pc_bot
DB_USER=your_username
DB_PASSWORD=your_password
```

5. Создайте базу данных PostgreSQL и выполните миграции:
```bash
psql -U your_username -d help_pc_bot -f database/schema.sql
```

## Структура проекта

```
Help_PC_bot/
├── bot.py              # Основной файл бота
├── database.py         # Функции для работы с базой данных
├── admin_panel.py      # Административная панель
├── database/          # SQL файлы и миграции
├── images/            # Изображения и музыка для обоев
├── requirements.txt   # Зависимости проекта
└── .env              # Конфигурационный файл
```

## Запуск

1. Активируйте виртуальное окружение (если еще не активировано):
```bash
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

2. Запустите бота:
```bash
python bot.py
```

## Использование

1. Найдите бота в Telegram по его username
2. Отправьте команду `/start` для начала работы
3. Используйте меню для навигации по функциям бота

### Основные команды

- `/start` - Запустить бота и открыть главное меню
- `/help` - Показать справку
- `/suggest` - Отправить предложение по улучшению бота
- `/my_suggestions` - Показать ваши предложения

## Разработка

### Добавление новых сборок

1. Подключитесь к базе данных
2. Добавьте новую сборку в таблицу `builds`
3. Добавьте компоненты сборки в таблицу `build_components`

### Добавление новых компонентов

1. Подключитесь к базе данных
2. Добавьте новый компонент в таблицу `components`

## Лицензия

MIT License

## Поддержка

Если у вас возникли вопросы или проблемы, создайте issue в репозитории проекта. 