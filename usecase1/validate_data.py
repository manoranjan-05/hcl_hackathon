"""Data quality validation rules"""
import sqlite3

def validate_headers(db_path='retail_db.sqlite'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Rule 1: Missing customer_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT transaction_id, customer_id, store_id, transaction_date, total_amount, 'REJECTED: Missing or NULL customer_id'
        FROM raw_store_sales_header
        WHERE (customer_id IS NULL OR customer_id = '' OR customer_id = 'INVALID')
        AND transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 2: Invalid store_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT r.transaction_id, r.customer_id, r.store_id, r.transaction_date, r.total_amount, 'REJECTED: Invalid store_id'
        FROM raw_store_sales_header r
        LEFT JOIN staging_stores s ON r.store_id = s.store_id
        WHERE s.store_id IS NULL
        AND r.transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 3: Invalid customer_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT r.transaction_id, r.customer_id, r.store_id, r.transaction_date, r.total_amount, 'REJECTED: Invalid customer_id'
        FROM raw_store_sales_header r
        LEFT JOIN staging_customer_details c ON r.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
        AND r.transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 4: Invalid transaction_date
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT transaction_id, customer_id, store_id, transaction_date, total_amount, 'REJECTED: Invalid transaction_date'
        FROM raw_store_sales_header
        WHERE (transaction_date IS NULL OR transaction_date = '')
        AND transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 5: Invalid total_amount
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT transaction_id, customer_id, store_id, transaction_date, total_amount, 'REJECTED: Invalid total_amount'
        FROM raw_store_sales_header
        WHERE total_amount <= 0
        AND transaction_id NOT IN (SELECT transaction_id FROM quarantine_rejected_sales_header)
    """)
    
    # Rule 10: Total mismatch
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_header 
        (transaction_id, customer_id, store_id, transaction_date, total_amount, rejection_reason)
        SELECT h.transaction_id, h.customer_id, h.store_id, h.transaction_date, h.total_amount, 'REJECTED: Total amount mismatch'
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

def validate_line_items(db_path='retail_db.sqlite'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Rule 6: Missing product_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, rejection_reason)
        SELECT line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, 'REJECTED: Missing product_id'
        FROM raw_store_sales_line_items
        WHERE (product_id IS NULL OR product_id = '')
        AND line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
    """)
    
    # Rule 7: Invalid product_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, rejection_reason)
        SELECT r.line_item_id, r.transaction_id, r.product_id, r.promotion_id, r.quantity, r.line_item_amount, 'REJECTED: Invalid product_id'
        FROM raw_store_sales_line_items r
        LEFT JOIN staging_products p ON r.product_id = p.product_id
        WHERE p.product_id IS NULL
        AND r.line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
    """)
    
    # Rule 8: Invalid line_item_amount
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, rejection_reason)
        SELECT line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, 'REJECTED: Invalid line_item_amount'
        FROM raw_store_sales_line_items
        WHERE line_item_amount <= 0
        AND line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
    """)
    
    # Rule 9: Invalid transaction_id
    cursor.execute("""
        INSERT INTO quarantine_rejected_sales_line_items 
        (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount, rejection_reason)
        SELECT r.line_item_id, r.transaction_id, r.product_id, r.promotion_id, r.quantity, r.line_item_amount, 'REJECTED: Invalid transaction_id'
        FROM raw_store_sales_line_items r
        LEFT JOIN raw_store_sales_header h ON r.transaction_id = h.transaction_id
        WHERE h.transaction_id IS NULL
        AND r.line_item_id NOT IN (SELECT line_item_id FROM quarantine_rejected_sales_line_items)
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Line items validation complete")

