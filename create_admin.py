import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Insert default admin if it doesn't exist
c.execute("SELECT * FROM users WHERE email=?", ("hope123@gmail.com",))
if not c.fetchone():
    c.execute("""
    INSERT INTO users (username, email, password, is_admin)
    VALUES (?, ?, ?, ?)
    """, ("admin", "hope123@gmail.com", "mwaura123", 1))
    print("Admin created!")
else:
    print("Admin already exists.")

conn.commit()
conn.close()