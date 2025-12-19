"""Route valid data to staging"""
import sqlite3

def route_valid_data(db_path='retail_db.sqlite'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear staging tables first (for re-running tests)
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

