from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("ID | Название | Цена | Категория")
for row in cursor.execute("SELECT id, name, total_price, price_category_id FROM pc_builds"):
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

conn.close() 