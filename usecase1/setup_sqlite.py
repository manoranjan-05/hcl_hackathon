"""
SQLite Setup Script
SQLite comes built-in with Python, but this script verifies installation and creates the database.
"""

import sqlite3
import sys
import os

def check_sqlite():
    """Check if SQLite is available"""
    try:
        conn = sqlite3.connect(':memory:')
        version = sqlite3.sqlite_version
        print(f"[OK] SQLite {version} is available")
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] SQLite check failed: {e}")
        return False

def create_database():
    """Create the retail database file"""
    db_path = 'retail_db.sqlite'
    if os.path.exists(db_path):
        print(f"[OK] Database {db_path} already exists")
    else:
        conn = sqlite3.connect(db_path)
        conn.close()
        print(f"[OK] Database {db_path} created")
    return db_path

if __name__ == "__main__":
    print("SQLite Setup")
    print("=" * 50)
    
    if check_sqlite():
        db_path = create_database()
        print(f"\n[OK] Setup complete! Database: {db_path}")
    else:
        print("\n[ERROR] Setup failed. Please install Python with SQLite support.")
        sys.exit(1)

