import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('kalyan.db')
cursor = connection.cursor()

def delete_table(table_name):
    try:
        # Use DROP TABLE to delete the table entirely
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        connection.commit()  # Save changes
        print(f"Table '{table_name}' has been deleted.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

# Example usage:
delete_table('kitchatapp_login')

# Close the connection
connection.close()
