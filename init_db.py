import sqlite3

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect('RapidXcel.db')

# Create the stocks table
conn.execute('''
CREATE TABLE IF NOT EXISTS stocks (
    stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
''')

# Insert some sample data
conn.execute('''
INSERT INTO stocks (stock_name, price, quantity) VALUES
('Product A', 100.0, 10),
('Product B', 200.0, 20),
('Product C', 300.0, 30)
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialized and table created successfully!")
