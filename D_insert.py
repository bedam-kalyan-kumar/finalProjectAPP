import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('kalyan.db')

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

try:
    # Add a new column 'gmail' to the table
    add_column_query = "ALTER TABLE kitchatapp_searchhistory ADD COLUMN searched_user TEXT"
    cursor.execute(add_column_query)

    # Commit the changes to the database
    connection.commit()

    print("Column 'gmail' added successfully to the 'login_project1' table.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # Close the database connection
    connection.close()
