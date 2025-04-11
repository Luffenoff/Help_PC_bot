FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта
COPY . .

# Создание и настройка базы данных
RUN python3 -c "from database import init_db; init_db()"

# Запуск бота
CMD ["python3", "bot.py"] 