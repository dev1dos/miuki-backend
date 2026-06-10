import sqlite3

DB_PATH = 'miuki.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            price       REAL    NOT NULL,
            description TEXT    DEFAULT '',
            image_url   TEXT    DEFAULT '',
            in_stock    INTEGER DEFAULT 1,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Тестовые товары
    test_products = [
        ('Pocky шоколадные', 'Азиатские снеки', 199, 'Классические японские шоколадные палочки', '', 1),
        ('Рамен Shin', 'Азиатские снеки', 149, 'Острая корейская лапша быстрого приготовления', '', 1),
        ('Тонер COSRX', 'Косметика', 890, 'Увлажняющий тонер с гиалуроновой кислотой', '', 1),
        ('Маска тканевая', 'Косметика', 250, 'Корейская тканевая маска для лица', '', 1),
        ('Фигурка Naruto', 'Игрушки', 1200, 'Коллекционная фигурка из аниме Наруто', '', 1),
        ('Мягкая игрушка Shiba', 'Игрушки', 650, 'Милая мягкая игрушка собачка Сиба-ину', '', 1),
        ('Блокнот Kawaii', 'Канцелярия', 350, 'Милый блокнот в японском стиле А5', '', 1),
        ('Набор стикеров', 'Канцелярия', 180, 'Декоративные стикеры в корейском стиле', '', 1),
        ('Парфюм Cherry Blossom', 'Туалетная вода', 2200, 'Нежный аромат японской сакуры', '', 1),
        ('Кольцо с жемчугом', 'Бижутерия', 450, 'Изящное кольцо в азиатском стиле', '', 1),
    ]

    conn.executemany(
        'INSERT OR IGNORE INTO products (name, category, price, description, image_url, in_stock) VALUES (?,?,?,?,?,?)',
        test_products
    )

    conn.commit()
    conn.close()
    print('База данных создана успешно!')


if __name__ == '__main__':
    init_db()
