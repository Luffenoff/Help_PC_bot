from database import add_dns_build_6

def add_new_build():
    """Добавление новой сборки в существующую базу данных"""
    build_id = add_dns_build_6()
    print(f"Новая сборка успешно добавлена с ID: {build_id}")

if __name__ == "__main__":
    add_new_build() 