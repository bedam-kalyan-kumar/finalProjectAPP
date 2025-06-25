import sqlite3

DB_PATH = 'kalyan.db'

def view_tables_and_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Tables in the database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Print column info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            cid, name, col_type, notnull, dflt_value, pk = col
            print(f"  - {name} ({col_type}) | NOT NULL: {notnull} | DEFAULT: {dflt_value} | PK: {pk}")

    conn.close()

if __name__ == "__main__":
    view_tables_and_schema(DB_PATH)
