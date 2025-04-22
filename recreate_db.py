import os
from database import init_db
from add_test_data import add_test_data

def recreate_database():
    """Пересоздание базы данных"""
    # Удаляем старую базу данных, если она существует
    if os.path.exists("bot_database.db"):
        os.remove("bot_database.db")
        print("Старая база данных удалена")
    
    # Инициализируем новую базу данных
    init_db()
    print("Новая база данных создана")
    
    # Добавляем тестовые данные
    add_test_data()
    print("Тестовые данные добавлены")
    
    print("База данных успешно пересоздана с тестовыми данными!")

if __name__ == "__main__":
    recreate_database() 