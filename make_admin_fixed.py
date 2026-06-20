import sqlite3

user_email = "hope123@gmail.com"

conn = sqlite3.connect("database.db")
c = conn.cursor()

# Promote user to admin
c.execute("UPDATE users SET is_admin = 1 WHERE email = hope123@gmail.com", (user_email,))
conn.commit()
conn.close()

print(f"User with email '{user_email}' is now an admin!")