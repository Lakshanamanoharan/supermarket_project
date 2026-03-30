import sqlite3

DB_FILE = "stock.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stock (
                 id INTEGER PRIMARY KEY,
                 product_name TEXT UNIQUE,
                 quantity REAL,
                 unit TEXT,
                 price_per_unit REAL)''')
    
    # Insert some mock data if empty
    c.execute("SELECT COUNT(*) FROM stock")
    if c.fetchone()[0] == 0:
        mock_data = [
            ('potato', 10.0, 'kg', 2.0),
            ('tomato', 5.0, 'kg', 3.0),
            ('onion', 20.0, 'kg', 1.5),
            ('milk', 15.0, 'liter', 1.2),
            ('bread', 30.0, 'pack', 2.5),
        ]
        c.executemany("INSERT INTO stock (product_name, quantity, unit, price_per_unit) VALUES (?, ?, ?, ?)", mock_data)
        conn.commit()
    conn.close()

def check_stock(product_name: str, requested_quantity: float):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT quantity, unit, price_per_unit FROM stock WHERE product_name LIKE ?", (f'%{product_name}%',))
    result = c.fetchone()
    conn.close()
    
    if result:
        available, unit, price = result
        return {
            "found": True,
            "product": product_name,
            "available_quantity": available,
            "requested_quantity": requested_quantity,
            "unit": unit,
            "price_per_unit": price,
            "can_fulfill": available >= requested_quantity
        }
    return {"found": False, "product": product_name}

def update_stock(product_name: str, quantity_to_deduct: float):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE stock SET quantity = quantity - ? WHERE product_name LIKE ? AND quantity >= ?", 
              (quantity_to_deduct, f'%{product_name}%', quantity_to_deduct))
    updated = c.rowcount > 0
    conn.commit()
    conn.close()
    return updated

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
