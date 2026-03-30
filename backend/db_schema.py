import sqlite3

try:
    conn = sqlite3.connect('../smart_assignment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("--- Database Schema ---")
    if not tables:
        print("No tables found in the database.")
    for table_name, table_sql in tables:
        print(f"Table: {table_name}")
        print(f"Schema: {table_sql}\n")
    conn.close()
except Exception as e:
    print(f"Error reading DB: {e}")
