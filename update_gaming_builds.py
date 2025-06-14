import re
import sqlite3

def get_block(url, txt):
    m = re.search(re.escape(url) + r'[\s\S]+?(?=\n\d+\.|\Z)', txt)
    return m.group(0) if m else ''

def extract_main(block):
    lines = [l.strip() for l in block.split('\n') if l.strip()]
    keys = ['Процессор', 'Материнская плата', 'Видеокарта', 'Оперативная память', 'Накопитель', 'Блок питания', 'Корпус', 'Кулер']
    out = []
    for k in keys:
        for l in lines:
            if l.startswith(k):
                l = l.replace('Компоненты:', '').strip()
                out.append(l)
                break
    return ' \n- '.join(out)

def main():
    db = sqlite3.connect('bot_database.db')
    cur = db.cursor()
    with open('sborki.txt', encoding='utf-8') as f:
        txt = f.read()
    builds = cur.execute('SELECT id, link FROM pc_builds WHERE device_type_id=1').fetchall()
    for id, link in builds:
        b = get_block(link.strip(), txt)
        desc = extract_main(b)
        if desc:
            cur.execute('UPDATE pc_builds SET description=? WHERE id=?', (desc, id))
    db.commit()
    print('Готово!')

if __name__ == '__main__':
    main() 