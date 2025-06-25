import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('kalyan.db')

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

# Specify the ID of the record to delete
record_id = 3  # Replace with the actual ID you want to delete

try:
    # Delete query
    delete_query = "DELETE FROM project1_login WHERE id = ?"
    cursor.execute(delete_query, (record_id,))

    # Commit the changes to the database
    connection.commit()

    # Check if the record was deleted
    if cursor.rowcount > 0:
        print(f"Record with ID {record_id} deleted successfully.")
    else:
        print(f"No record found with ID {record_id}.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # Close the database connection
    connection.close()
