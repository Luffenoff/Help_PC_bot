from database import add_dns_build_4

if __name__ == "__main__":
    build_id = add_dns_build_4()
    print(f"Сборка успешно добавлена в базу данных. ID сборки: {build_id}") 