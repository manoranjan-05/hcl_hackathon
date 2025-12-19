"""Use Case 6: Inventory and Store Performance Correlation"""
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import get_connection

def analyze_inventory_performance(db_path):
    """Analyze inventory levels and correlate with sales performance"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear previous analysis
    cursor.execute("DELETE FROM inventory_analysis")
    
    # Get top 5 best-selling products overall
    cursor.execute("""
        SELECT 
            li.product_id,
            SUM(li.quantity) as total_quantity_sold,
            SUM(li.line_item_amount) as total_revenue
        FROM staging_store_sales_line_items li
        GROUP BY li.product_id
        ORDER BY total_quantity_sold DESC
        LIMIT 5
    """)
    
    top_products = cursor.fetchall()
    
    print("\nTop 5 Best-Selling Products:")
    print("-" * 60)
    
    # For each top product, analyze inventory across stores
    for product_id, total_qty, total_revenue in top_products:
        # Get product info
        cursor.execute("""
            SELECT product_name, product_category, current_stock_level
            FROM staging_products
            WHERE product_id = ?
        """, (product_id,))
        
        product_info = cursor.fetchone()
        if not product_info:
            continue
        
        product_name, category, current_stock = product_info
        
        print(f"\n{product_name} ({product_id})")
        print(f"  Total Sold: {total_qty} units, Revenue: ${total_revenue:.2f}")
        
        # Get sales by store for this product
        cursor.execute("""
            SELECT 
                h.store_id,
                COUNT(DISTINCT DATE(h.transaction_date)) as days_with_sales,
                SUM(li.quantity) as total_sold,
                AVG(li.quantity) as avg_daily_sales
            FROM staging_store_sales_line_items li
            JOIN staging_store_sales_header h ON li.transaction_id = h.transaction_id
            WHERE li.product_id = ?
            GROUP BY h.store_id
        """, (product_id,))
        
        store_sales = cursor.fetchall()
        
        # Get total days in analysis period
        cursor.execute("""
            SELECT COUNT(DISTINCT DATE(transaction_date)) as total_days
            FROM staging_store_sales_header
        """)
        total_days = cursor.fetchone()[0] or 1
        
        # Analyze each store
        for store_id, days_with_sales, total_sold, avg_daily_sales in store_sales:
            # Calculate out-of-stock days
            # Assume product is out of stock if current_stock_level is 0
            # In a real system, we'd have daily inventory snapshots
            out_of_stock_days = 0
            if current_stock == 0:
                # If current stock is 0, estimate based on sales pattern
                # Assume it was out of stock on days without sales
                out_of_stock_days = total_days - days_with_sales
            
            out_of_stock_percentage = (out_of_stock_days / total_days * 100) if total_days > 0 else 0
            
            # Estimate lost sales
            # Use average daily sales for days out of stock
            estimated_lost_sales = avg_daily_sales * out_of_stock_days if avg_daily_sales else 0
            
            # Insert analysis
            cursor.execute("""
                INSERT INTO inventory_analysis
                (product_id, store_id, total_days, out_of_stock_days, 
                 out_of_stock_percentage, estimated_lost_sales)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (product_id, store_id, total_days, out_of_stock_days, 
                  out_of_stock_percentage, estimated_lost_sales))
            
            print(f"  Store {store_id}:")
            print(f"    Days with Sales: {days_with_sales}/{total_days}")
            print(f"    Out of Stock Days: {out_of_stock_days} ({out_of_stock_percentage:.1f}%)")
            print(f"    Estimated Lost Sales: ${estimated_lost_sales:.2f}")
    
    conn.commit()
    conn.close()
    
    print("\n[OK] Inventory performance analysis complete")
    return len(top_products)

def execute(db_path):
    """Execute Use Case 6 pipeline"""
    print("\n" + "="*60)
    print("USE CASE 6: INVENTORY AND STORE PERFORMANCE CORRELATION")
    print("="*60)
    
    count = analyze_inventory_performance(db_path)
    print(f"\n[OK] Use Case 6 completed successfully - {count} products analyzed")
    return count

