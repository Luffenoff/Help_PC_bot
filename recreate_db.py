import os
from database import init_db

def recreate_database():
    """Пересоздание базы данных"""
    # Удаляем старую базу данных, если она существует
    if os.path.exists("bot_database.db"):
        os.remove("bot_database.db")
        print("Старая база данных удалена")
    
    # Инициализируем новую базу данных
    init_db()
    print("Новая база данных создана")

if __name__ == "__main__":
    recreate_database() 