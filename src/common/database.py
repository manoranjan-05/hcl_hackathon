"""Database setup and connection utilities"""
import sqlite3
import os

def get_db_path(db_name='retail_db.sqlite'):
    """Get database path relative to project root"""
    # Get project root (parent of src)
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, db_name)

def setup_database(db_path=None):
    """Setup database with all required tables"""
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Master data tables (staging schema)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging_stores (
            store_id TEXT PRIMARY KEY,
            store_name TEXT,
            store_city TEXT,
            store_region TEXT,
            opening_date TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging_products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            product_category TEXT,
            unit_price REAL,
            current_stock_level INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging_customer_details (
            customer_id TEXT PRIMARY KEY,
            first_name TEXT,
            email TEXT,
            loyalty_status TEXT,
            total_loyalty_points INTEGER DEFAULT 0,
            last_purchase_date TEXT,
            segment_id TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging_promotion_details (
            promotion_id TEXT PRIMARY KEY,
            promotion_name TEXT,
            start_date TEXT,
            end_date TEXT,
            discount_percentage REAL,
            applicable_category TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staging_loyalty_rules (
            rule_id INTEGER PRIMARY KEY,
            rule_name TEXT,
            points_per_unit_spend REAL,
            min_spend_threshold REAL,
            bonus_points INTEGER
        )
    """)
    
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
    
    # Use Case 2: Promotion effectiveness results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promotion_effectiveness (
            promotion_id TEXT PRIMARY KEY,
            promotion_name TEXT,
            category TEXT,
            baseline_sales REAL,
            promoted_sales REAL,
            sales_lift_percentage REAL,
            rank INTEGER
        )
    """)
    
    # Use Case 3: Loyalty point transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loyalty_point_transactions (
            transaction_id TEXT PRIMARY KEY,
            customer_id TEXT,
            transaction_amount REAL,
            points_earned INTEGER,
            rule_applied TEXT,
            transaction_date TEXT
        )
    """)
    
    # Use Case 4: Customer segments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_segments (
            customer_id TEXT PRIMARY KEY,
            segment_name TEXT,
            recency_days INTEGER,
            frequency INTEGER,
            monetary_value REAL,
            loyalty_points INTEGER,
            segment_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Use Case 5: Notifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loyalty_notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            email TEXT,
            subject TEXT,
            body TEXT,
            points_earned INTEGER,
            total_points INTEGER,
            status TEXT DEFAULT 'pending',
            created_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Use Case 6: Inventory analysis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_analysis (
            product_id TEXT,
            store_id TEXT,
            total_days INTEGER,
            out_of_stock_days INTEGER,
            out_of_stock_percentage REAL,
            estimated_lost_sales REAL,
            analysis_date TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (product_id, store_id)
        )
    """)
    
    conn.commit()
    conn.close()
    return db_path

def get_connection(db_path=None):
    """Get database connection"""
    if db_path is None:
        db_path = get_db_path()
    return sqlite3.connect(db_path)

