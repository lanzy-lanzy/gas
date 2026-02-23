import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if password column exists
    cursor.execute("PRAGMA table_info(core_pendingregistration)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'password' not in columns:
        # Add password column
        cursor.execute("ALTER TABLE core_pendingregistration ADD COLUMN password VARCHAR(255)")
        conn.commit()
        print("Password column added successfully!")
    else:
        print("Password column already exists")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
