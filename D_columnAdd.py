import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('kalyan.db')  # Replace with your database file name
cursor = connection.cursor()

# Add the 'last_login' column to the 'project1_login' table
add_last_login_column_query = """
ALTER TABLE project1_login
ADD COLUMN last_login TEXT;
"""

try:
    # Execute the SQL command to add the 'last_login' column
    cursor.execute(add_last_login_column_query)
    print("Column 'last_login' added successfully to the 'project1_login' table.")
    
    # Commit the changes
    connection.commit()
except sqlite3.OperationalError as e:
    print(f"Error: {e}")
finally:
    # Close the connection
    connection.close()
