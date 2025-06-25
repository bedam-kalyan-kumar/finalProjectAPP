import sqlite3

# Connect to your kalyan.db
conn = sqlite3.connect('kalyan.db')
cursor = conn.cursor()

# Create login table
cursor.execute("DROP TABLE login")

print("Table 'login' created successfully.")

# Commit changes and close connection
conn.commit()
conn.close()
