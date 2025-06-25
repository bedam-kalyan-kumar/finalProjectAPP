import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('kalyan.db')
cursor = conn.cursor()

# Optional: Pretty print output
print("{:<5} {:<10} {:<30} {:<25}".format("ID", "User ID", "Query", "Created At"))
print("-" * 75)

# Query the data
cursor.execute("SELECT id, user_id, query, created_at FROM kitchatapp_searchhistory")
rows = cursor.fetchall()

# Display each row
for row in rows:
    print("{:<5} {:<10} {:<30} {:<25}".format(row[0], row[1], row[2], row[3]))

# Close the connection
conn.close()
