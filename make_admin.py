import sqlite3

# Replace with your user's email
user_email = "hope123@gmail.com"

# Connect to your database
conn = sqlite3.connect("database.db")
c = conn.cursor()

# Update the user to be admin
c.execute("UPDATE users SET is_admin = 1 WHERE email = hope123@gmail.com", (user_email,))
conn.commit()
conn.close()

print(f"User with email '{user_email}' is now an admin!")