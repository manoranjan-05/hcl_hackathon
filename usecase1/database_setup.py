"""Database setup: Create schemas and tables"""
import sqlite3

def setup_db(db_path='retail_db.sqlite'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQLite doesn't support schemas, so we use table prefixes
    # Raw tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_store_sales_header (
            transaction_id TEXT PRIMARY KEY,
            customer_id TEXT,
            store_id TEXT,
            transaction_date TEXT,
            total_amount REAL,
            load_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_store_sales_line_items (
            line_item_id INTEGER PRIMARY KEY,
            transaction_id TEXT,
            product_id TEXT,
            promotion_id TEXT,
            quantity INTEGER,
            line_item_amount REAL,
            load_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Quarantine tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quarantine_rejected_sales_header (
            transaction_id TEXT PRIMARY KEY,
            customer_id TEXT,
            store_id TEXT,
            transaction_date TEXT,
            total_amount REAL,
            rejection_reason TEXT,
            rejection_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quarantine_rejected_sales_line_items (
            line_item_id INTEGER PRIMARY KEY,
            transaction_id TEXT,
            product_id TEXT,
            promotion_id TEXT,
            quantity INTEGER,
            line_item_amount REAL,
            rejection_reason TEXT,
            rejection_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Staging tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging_store_sales_header (
            transaction_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            store_id TEXT NOT NULL,
            transaction_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            processed INTEGER DEFAULT 0,
            created_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging_store_sales_line_items (
            line_item_id INTEGER PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            promotion_id TEXT,
            quantity INTEGER NOT NULL,
            line_item_amount REAL NOT NULL,
            created_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Database tables created")

