import sqlite3

# Connect to the SQLite database (replace 'kalyan.db' with the correct database file path)
conn = sqlite3.connect('kalyan.db')
cursor = conn.cursor()

# SQL command to create the 'posts' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    caption TEXT,
    likes_count INTEGER NOT NULL DEFAULT 0,
    comments_count INTEGER NOT NULL DEFAULT 0,
    shares_count INTEGER NOT NULL DEFAULT 0,
    image TEXT,
    video TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Table 'posts' created successfully!")
