import sqlite3

# Connect to SQLite DB (or create if not exists)
conn = sqlite3.connect("example.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    signup_date DATE
)
""")

# Insert some sample data
cursor.executemany("""
INSERT INTO customers (id,name, email, signup_date)
VALUES (?,?, ?, ?)
""", [
    (1,"Alice Johnson", "alice@example.com", "2025-06-15"),
    (2,"Bob Smith", "bob@example.com", "2024-07-01"),
    (3,"Clara White", "clara@example.com", "2024-07-10")
])

conn.commit()
conn.close()
