import sqlite3

DB_FILE = "stock.db"

# List of 200 real supermarket products in India with estimated INR prices
products = [
    # Vegetables
    ("tomato", 50.0, "kg", 40.0),
    ("onion", 100.0, "kg", 35.0),
    ("potato", 200.0, "kg", 30.0),
    ("carrot", 30.0, "kg", 50.0),
    ("cabbage", 20.0, "kg", 40.0),
    ("cauliflower", 15.0, "piece", 45.0),
    ("brinjal", 25.0, "kg", 40.0),
    ("lady finger", 15.0, "kg", 60.0),
    ("capsicum", 10.0, "kg", 80.0),
    ("green chilli", 5.0, "kg", 100.0),
    ("ginger", 5.0, "kg", 120.0),
    ("garlic", 10.0, "kg", 150.0),
    ("coriander leaves", 20.0, "bunch", 15.0),
    ("mint leaves", 20.0, "bunch", 10.0),
    ("curry leaves", 50.0, "bunch", 5.0),
    ("lemon", 100.0, "piece", 4.0),
    ("beetroot", 25.0, "kg", 45.0),
    ("cucumber", 40.0, "kg", 30.0),
    ("radish", 15.0, "kg", 30.0),
    ("bitter gourd", 10.0, "kg", 55.0),
    ("bottle gourd", 20.0, "piece", 35.0),
    ("snake gourd", 15.0, "piece", 30.0),
    ("ash gourd", 10.0, "kg", 40.0),
    ("pumpkin", 20.0, "kg", 25.0),
    ("drumstick", 50.0, "piece", 8.0),
    ("beans", 15.0, "kg", 80.0),
    ("broad beans", 10.0, "kg", 75.0),
    ("cluster beans", 12.0, "kg", 65.0),
    ("sweet potato", 15.0, "kg", 40.0),
    ("yam", 10.0, "kg", 50.0),

    # Fruits
    ("apple", 50.0, "kg", 180.0),
    ("banana", 100.0, "dozen", 60.0),
    ("orange", 40.0, "kg", 80.0),
    ("grapes", 20.0, "kg", 120.0),
    ("mango", 30.0, "kg", 150.0),
    ("papaya", 15.0, "piece", 50.0),
    ("watermelon", 20.0, "piece", 70.0),
    ("muskmelon", 15.0, "piece", 50.0),
    ("pomegranate", 20.0, "kg", 200.0),
    ("pineapple", 15.0, "piece", 60.0),
    ("guava", 25.0, "kg", 60.0),
    ("sapota", 20.0, "kg", 70.0),
    ("sweet lime", 30.0, "kg", 80.0),
    ("kiwi", 50.0, "piece", 30.0),
    ("pear", 15.0, "kg", 160.0),
    ("plum", 10.0, "kg", 200.0),
    ("peach", 10.0, "kg", 180.0),
    ("strawberry", 10.0, "box", 100.0),
    ("cherry", 5.0, "box", 150.0),
    ("dragon fruit", 10.0, "piece", 80.0),

    # Staples: Rice, Wheat, Flours
    ("basmati rice", 100.0, "kg", 110.0),
    ("raw rice", 200.0, "kg", 60.0),
    ("boiled rice", 200.0, "kg", 55.0),
    ("idli rice", 150.0, "kg", 50.0),
    ("brown rice", 50.0, "kg", 90.0),
    ("wheat flour", 150.0, "kg", 45.0),
    ("maida", 50.0, "kg", 40.0),
    ("rice flour", 40.0, "kg", 50.0),
    ("besan", 30.0, "kg", 90.0),
    ("rava", 40.0, "kg", 55.0),
    ("semiya", 50.0, "packet", 25.0),
    ("poha", 30.0, "kg", 60.0),
    ("sabudana", 20.0, "kg", 80.0),

    # Pulses and Dals
    ("toor dal", 50.0, "kg", 160.0),
    ("urad dal", 40.0, "kg", 150.0),
    ("moong dal", 50.0, "kg", 130.0),
    ("chana dal", 40.0, "kg", 90.0),
    ("masoor dal", 30.0, "kg", 100.0),
    ("rajma", 20.0, "kg", 140.0),
    ("green gram", 30.0, "kg", 120.0),
    ("black chickpea", 25.0, "kg", 95.0),
    ("white chickpea", 30.0, "kg", 120.0),
    ("horse gram", 15.0, "kg", 85.0),
    ("soya chunks", 20.0, "kg", 100.0),

    # Oil & Ghee
    ("sunflower oil", 100.0, "liter", 120.0),
    ("groundnut oil", 50.0, "liter", 180.0),
    ("mustard oil", 40.0, "liter", 150.0),
    ("gingelly oil", 30.0, "liter", 250.0),
    ("coconut oil", 40.0, "liter", 220.0),
    ("olive oil", 15.0, "liter", 800.0),
    ("ghee", 30.0, "liter", 600.0),
    ("butter", 50.0, "packet", 55.0),
    ("paneer", 30.0, "packet", 85.0),
    ("cheese", 40.0, "packet", 120.0),

    # Spices & Condiments
    ("salt", 200.0, "kg", 25.0),
    ("rock salt", 50.0, "kg", 30.0),
    ("sugar", 150.0, "kg", 45.0),
    ("jaggery", 50.0, "kg", 70.0),
    ("turmeric powder", 30.0, "kg", 200.0),
    ("chilli powder", 40.0, "kg", 250.0),
    ("coriander powder", 30.0, "kg", 180.0),
    ("cumin powder", 15.0, "kg", 400.0),
    ("garam masala", 20.0, "packet", 40.0),
    ("sambar powder", 25.0, "packet", 50.0),
    ("rasam powder", 20.0, "packet", 45.0),
    ("mustard seeds", 15.0, "kg", 100.0),
    ("cumin seeds", 20.0, "kg", 350.0),
    ("fenugreek seeds", 10.0, "kg", 120.0),
    ("fennel seeds", 10.0, "kg", 250.0),
    ("black pepper", 15.0, "kg", 700.0),
    ("cloves", 5.0, "kg", 1200.0),
    ("cardamom", 5.0, "kg", 3000.0),
    ("cinnamon", 5.0, "kg", 500.0),
    ("asafoetida", 30.0, "box", 65.0),
    ("tamarind", 25.0, "kg", 150.0),

    # Dairy & Eggs
    ("milk", 200.0, "liter", 50.0),
    ("curd", 100.0, "packet", 35.0),
    ("egg", 500.0, "piece", 6.0),
    ("yogurt", 30.0, "cup", 25.0),
    ("ice cream", 20.0, "tub", 200.0),

    # Beverages
    ("tea dust", 50.0, "kg", 400.0),
    ("coffee powder", 30.0, "kg", 500.0),
    ("green tea", 20.0, "box", 150.0),
    ("health drink powder", 40.0, "jar", 300.0),
    ("mineral water", 100.0, "bottle", 20.0),
    ("apple juice", 30.0, "bottle", 100.0),
    ("mango juice", 30.0, "bottle", 90.0),
    ("orange juice", 30.0, "bottle", 95.0),
    ("coca cola", 50.0, "bottle", 40.0),
    ("pepsi", 50.0, "bottle", 40.0),
    ("sprite", 40.0, "bottle", 40.0),

    # Snacks & Sweets
    ("biscuits", 200.0, "packet", 20.0),
    ("cookies", 100.0, "packet", 40.0),
    ("potato chips", 150.0, "packet", 10.0),
    ("namkeen", 100.0, "packet", 50.0),
    ("mixtures", 80.0, "packet", 60.0),
    ("murukku", 50.0, "packet", 40.0),
    ("chocolates", 200.0, "piece", 10.0),
    ("candies", 300.0, "packet", 30.0),
    ("dates", 30.0, "box", 150.0),
    ("peanuts", 40.0, "kg", 120.0),
    ("cashew nuts", 20.0, "kg", 800.0),
    ("almonds", 25.0, "kg", 700.0),
    ("raisins", 20.0, "kg", 300.0),
    ("pistachios", 15.0, "kg", 1000.0),
    ("walnuts", 10.0, "kg", 1200.0),

    # Household & Cleaning
    ("washing powder", 60.0, "kg", 100.0),
    ("detergent bar", 100.0, "piece", 20.0),
    ("dish wash bar", 80.0, "piece", 15.0),
    ("dish wash liquid", 40.0, "bottle", 110.0),
    ("floor cleaner", 30.0, "bottle", 90.0),
    ("toilet cleaner", 40.0, "bottle", 85.0),
    ("glass cleaner", 20.0, "bottle", 80.0),
    ("bathing soap", 120.0, "piece", 35.0),
    ("shampoo", 80.0, "bottle", 150.0),
    ("conditioner", 30.0, "bottle", 160.0),
    ("toothpaste", 100.0, "tube", 60.0),
    ("toothbrush", 80.0, "piece", 25.0),
    ("hand wash", 50.0, "bottle", 80.0),
    ("body lotion", 25.0, "bottle", 200.0),
    ("coconut hair oil", 40.0, "bottle", 90.0),
    ("talcum powder", 30.0, "box", 100.0),
    ("shaving cream", 40.0, "tube", 75.0),
    ("razor", 60.0, "piece", 50.0),
    ("sanitary pads", 50.0, "packet", 80.0),
    ("diapers", 30.0, "packet", 400.0),
    ("tissue paper", 80.0, "box", 60.0),
    ("toilet roll", 50.0, "roll", 30.0),
    ("aluminium foil", 40.0, "roll", 120.0),
    ("garbage bags", 50.0, "packet", 60.0),
    ("match box", 200.0, "packet", 5.0),
    ("mosquito repellent liquid", 40.0, "bottle", 85.0),
    ("mosquito coils", 50.0, "box", 40.0),
    ("room freshener", 20.0, "bottle", 140.0),
    ("shoe polish", 15.0, "box", 60.0),

    # Bakery
    ("bread", 60.0, "packet", 35.0),
    ("buns", 40.0, "packet", 20.0),
    ("rusk", 50.0, "packet", 40.0),
    ("cake", 20.0, "piece", 30.0),
    ("muffins", 30.0, "piece", 15.0),
    ("pizza base", 20.0, "packet", 45.0),

    # Meat & Seafood (Optional depending on supermarket)
    ("chicken", 50.0, "kg", 220.0),
    ("mutton", 20.0, "kg", 800.0),
    ("fish", 30.0, "kg", 300.0),
    ("prawns", 15.0, "kg", 500.0)
]

def seed_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS stock")
    c.execute('''CREATE TABLE stock (
                 id INTEGER PRIMARY KEY,
                 product_name TEXT UNIQUE,
                 quantity REAL,
                 unit TEXT,
                 price_per_unit REAL)''')
                 
    c.executemany("INSERT INTO stock (product_name, quantity, unit, price_per_unit) VALUES (?, ?, ?, ?)", products)
    conn.commit()
    conn.close()
    print(f"Successfully seeded {len(products)} products into {DB_FILE}!")

if __name__ == "__main__":
    seed_db()
