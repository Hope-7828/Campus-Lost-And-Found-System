import sqlite3
from tabulate import tabulate

conn = sqlite3.connect('database.db')
c = conn.cursor()

#  USERS TABLE
print("=== USERS TABLE ===")
c.execute("SELECT * FROM users")
users = c.fetchall()
if users:
    print(tabulate(users, headers=["ID", "Username", "Email", "Password"], tablefmt="grid"))
else: 
    print("No data in USERS table.")

#  LOST ITEMS TABLE
print("\n=== LOST ITEMS TABLE ===")
c.execute("SELECT * FROM lost_items")
lost_items = c.fetchall()
if lost_items:
    print(tabulate(lost_items, headers=["ID", "User ID", "Item Name", "Description", "Image"], tablefmt="grid"))
else:
    print("No data in LOST ITEMS table.")

# FOUND ITEMS TABLE 
print("\n=== FOUND ITEMS TABLE ===")
c.execute("SELECT * FROM found_items")
found_items = c.fetchall()
if found_items:
    print(tabulate(found_items, headers=["ID", "User ID", "Item Name", "Description", "Image"], tablefmt="grid"))
else:
    print("No data in FOUND ITEMS table.")

# MESSAGES TABLE
print("\n=== MESSAGES TABLE ===")
c.execute("SELECT * FROM messages")
messages = c.fetchall()
if messages:
    print(tabulate(messages, headers=["ID", "Sender ID", "Receiver ID", "Item ID", "Message", "Timestamp"], tablefmt="grid"))
else:
    print("No data in MESSAGES table.")

conn.close()
