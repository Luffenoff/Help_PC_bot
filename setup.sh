#!/bin/bash

# Обновление системы
echo "Обновление системы..."
sudo apt-get update
sudo apt-get upgrade -y

# Установка Python и pip если их нет
echo "Установка Python и pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Установка Chrome и ChromeDriver
echo "Установка Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
rm google-chrome-stable_current_amd64.deb

# Создание виртуального окружения
echo "Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей Python..."
pip install -r requirements.txt

# Создание .env файла если его нет
if [ ! -f .env ]; then
    echo "Создание файла .env..."
    echo "BOT_TOKEN=your_telegram_bot_token" > .env
    echo "Пожалуйста, замените 'your_telegram_bot_token' в файле .env на ваш токен бота"
fi

# Создание директории для кэша
echo "Создание директории для кэша..."
mkdir -p cache

echo "Установка завершена!"
echo "Теперь выполните следующие действия:"
echo "1. Отредактируйте файл .env и вставьте ваш токен бота"
echo "2. Запустите бота командой: python3 new_bot.py" 