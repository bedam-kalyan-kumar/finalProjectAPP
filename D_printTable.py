import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('kalyan.db')
cursor = connection.cursor()

def list_all_tables():
    try:
        # Query the sqlite_master table for table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if tables:
            print("Tables in the database:")
            for table in tables:
                print(table[0])
        else:
            print("No tables found in the database.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

# Example usage:
list_all_tables()

# Close the connection
connection.close()
