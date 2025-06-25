import sqlite3

conn = sqlite3.connect('kalyan.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(kitchatapp_login);")
columns_info = cursor.fetchall()

print("Table 'kitchatapp_searchhistory' columns:")
for col in columns_info:
    cid, name, ctype, notnull, dflt_value, pk = col
    print(f"Column ID: {cid}, Name: {name}, Type: {ctype}, Not Null: {notnull}, Default: {dflt_value}, Primary Key: {pk}")

conn.close()
