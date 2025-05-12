import os
from database import init_db

def recreate_database():
    """Пересоздание базы данных"""
    # Удаляем существующую базу данных
    if os.path.exists("bot_database.db"):
        os.remove("bot_database.db")
        print("Старая база данных удалена")
    
    # Создаем новую базу данных
    init_db()
    print("База данных успешно пересоздана")

if __name__ == "__main__":
    recreate_database() 