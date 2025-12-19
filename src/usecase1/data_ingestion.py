"""Use Case 1: Data Ingestion and Quality Validation"""
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import get_connection
from common.data_loader import load_master_data, load_raw_sales_data

def normalize_data(db_path):
    """Normalize data (1NF, 2NF, 3NF)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1NF: Split multi-value product_ids in line items
    # Check if there are any comma-separated product_ids
    cursor.execute("""
        SELECT line_item_id, product_id, quantity, line_item_amount, transaction_id
        FROM raw_store_sales_line_items
        WHERE product_id LIKE '%,%'
    """)
    
    multi_value_items = cursor.fetchall()
    if multi_value_items:
        for item in multi_value_items:
            line_item_id, product_ids_str, qty, amount, txn_id = item
            product_ids = [p.strip() for p in product_ids_str.split(',')]
            
            # Delete original record
            cursor.execute("DELETE FROM raw_store_sales_line_items WHERE line_item_id = ?", (line_item_id,))
            
            # Insert split records
            per_product_amount = amount / len(product_ids)
            per_product_qty = qty // len(product_ids)
            remainder_qty = qty % len(product_ids)
            
            for idx, pid in enumerate(product_ids):
                new_line_item_id = line_item_id * 1000 + idx  # Create unique ID
                new_qty = per_product_qty + (1 if idx < remainder_qty else 0)
                new_amount = per_product_amount
                
                cursor.execute("""
                    INSERT INTO raw_store_sales_line_items 
                    (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount)
                    VALUES (?, ?, ?, NULL, ?, ?)
                """, (new_line_item_id, txn_id, pid, new_qty, new_amount))
    
    conn.commit()
    conn.close()
    print("[OK] Data normalization complete")

def validate_headers(db_path):
    """Validate header records"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Rule 1: Missing customer_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT transaction_id, customer_id, store_id, transaction_date, total_amount, 
               'REJECTED: Missing or NULL customer_id'
        FROM raw_store_sales_header
        WHERE (customer_id IS NULL OR customer_id = '' OR customer_id = 'INVALID')
        AND transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 2: Invalid store_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT r.transaction_id, r.customer_id, r.store_id, r.transaction_date, r.total_amount, 
               'REJECTED: Invalid store_id'
        FROM raw_store_sales_header r
        LEFT JOIN staging_stores s ON r.store_id = s.store_id
        WHERE s.store_id IS NULL
        AND r.transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 3: Invalid customer_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT r.transaction_id, r.customer_id, r.store_id, r.transaction_date, r.total_amount, 
               'REJECTED: Invalid customer_id'
        FROM raw_store_sales_header r
        LEFT JOIN staging_customer_details c ON r.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
        AND r.transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 4: Invalid transaction_date
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT transaction_id, customer_id, store_id, transaction_date, total_amount, 
               'REJECTED: Invalid transaction_date'
        FROM raw_store_sales_header
        WHERE (transaction_date IS NULL OR transaction_date = '')
        AND transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 5: Invalid total_amount
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT transaction_id, customer_id, store_id, transaction_date, total_amount, 
               'REJECTED: Invalid total_amount'
        FROM raw_store_sales_header
        WHERE total_amount <= 0
        AND transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 10: Total mismatch
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT h.transaction_id, h.customer_id, h.store_id, h.transaction_date, h.total_amount, 
               'REJECTED: Total amount mismatch'
        FROM raw_store_sales_header h
        LEFT JOIN (
            SELECT transaction_id, SUM(line_item_amount) as total
            FROM raw_store_sales_line_items
            GROUP BY transaction_id
        ) l ON h.transaction_id = l.transaction_id
        WHERE ABS(h.total_amount - COALESCE(l.total, 0)) > 0.01
        AND h.transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Header validation complete")

def validate_line_items(db_path):
    """Validate line item records"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Rule 6: Missing product_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, rejection_reason)
        SELECT line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, 
               'REJECTED: Missing product_id'
        FROM raw_store_sales_line_items
        WHERE (product_id IS NULL OR product_id = '')
        AND line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
    """)
    
    # Rule 7: Invalid product_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, rejection_reason)
        SELECT r.line_item_id, r.transaction_id, r.product_id, r.promotion_id, r.quantity, r.line_item_amount, 
               'REJECTED: Invalid product_id'
        FROM raw_store_sales_line_items r
        LEFT JOIN staging_products p ON r.product_id = p.product_id
        WHERE p.product_id IS NULL
        AND r.line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
    """)
    
    # Rule 8: Invalid line_item_amount
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, rejection_reason)
        SELECT line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, 
               'REJECTED: Invalid line_item_amount'
        FROM raw_store_sales_line_items
        WHERE line_item_amount <= 0
        AND line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
    """)
    
    # Rule 9: Invalid transaction_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, rejection_reason)
        SELECT r.line_item_id, r.transaction_id, r.product_id, r.promotion_id, r.quantity, r.line_item_amount, 
               'REJECTED: Invalid transaction_id'
        FROM raw_store_sales_line_items r
        LEFT JOIN raw_store_sales_header h ON r.transaction_id = h.transaction_id
        WHERE h.transaction_id IS NULL
        AND r.line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Line items validation complete")

def route_valid_data(db_path):
    """Route valid data to staging"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear staging tables
    cursor.execute("DELETE FROM staging_store_sales_line_items")
    cursor.execute("DELETE FROM staging_store_sales_header")
    
    # Route valid headers
    cursor.execute("""
        INSERT INTO staging_store_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount)
        SELECT transaction_id, customer_id, store_id, transaction_date, total_amount
        FROM raw_store_sales_header
        WHERE transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Route valid line items
    cursor.execute("""
        INSERT INTO staging_store_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount)
        SELECT r.line_item_id, r.transaction_id, r.product_id, r.promotion_id, r.quantity, r.line_item_amount
        FROM raw_store_sales_line_items r
        WHERE r.line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
        AND r.transaction_id IN (SELECT transaction_id FROM staging_store_sales_header)
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Valid data routed to staging")

def execute(db_path):
    """Execute Use Case 1 pipeline"""
    print("\n" + "="*60)
    print("USE CASE 1: DATA INGESTION AND QUALITY VALIDATION")
    print("="*60)
    
    # Load master data
    print("\n[Step 1] Loading master data...")
    load_master_data(db_path)
    
    # Load raw sales data
    print("\n[Step 2] Loading raw sales data...")
    load_raw_sales_data(db_path)
    
    # Normalize data
    print("\n[Step 3] Normalizing data...")
    normalize_data(db_path)
    
    # Validate headers
    print("\n[Step 4] Validating header data...")
    validate_headers(db_path)
    
    # Validate line items
    print("\n[Step 5] Validating line items...")
    validate_line_items(db_path)
    
    # Route valid data
    print("\n[Step 6] Routing valid data to staging...")
    route_valid_data(db_path)
    
    print("\n[OK] Use Case 1 completed successfully")
    return db_path

