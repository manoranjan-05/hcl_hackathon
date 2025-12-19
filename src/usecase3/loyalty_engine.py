"""Use Case 3: Loyalty Point Calculation Engine"""
import sqlite3
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import get_connection

def calculate_loyalty_points(db_path):
    """Calculate and accrue loyalty points for transactions"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear previous loyalty transactions
    cursor.execute("DELETE FROM loyalty_point_transactions")
    
    # Get all unprocessed transactions
    cursor.execute("""
        SELECT h.transaction_id, h.customer_id, h.total_amount, h.transaction_date
        FROM staging_store_sales_header h
        WHERE h.processed = 0
    """)
    
    transactions = cursor.fetchall()
    
    # Get loyalty rules
    cursor.execute("""
        SELECT rule_id, rule_name, points_per_unit_spend, min_spend_threshold, bonus_points
        FROM staging_loyalty_rules
        ORDER BY min_spend_threshold DESC
    """)
    
    rules = cursor.fetchall()
    
    total_points_updated = 0
    
    for txn_id, customer_id, total_amount, txn_date in transactions:
        # Find applicable rule (highest threshold that is met)
        applicable_rule = None
        for rule_id, rule_name, points_per_unit, min_spend, bonus_points in rules:
            if total_amount >= min_spend:
                applicable_rule = (rule_id, rule_name, points_per_unit, min_spend, bonus_points)
                break
        
        if applicable_rule:
            rule_id, rule_name, points_per_unit, min_spend, bonus_points = applicable_rule
            
            # Calculate points
            base_points = int(total_amount * points_per_unit)
            total_points_earned = base_points + bonus_points
            
            # Record transaction
            cursor.execute("""
                INSERT INTO loyalty_point_transactions
                (transaction_id, customer_id, transaction_amount, points_earned, rule_applied, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (txn_id, customer_id, total_amount, total_points_earned, rule_name, txn_date))
            
            # Update customer's total points
            cursor.execute("""
                UPDATE staging_customer_details
                SET total_loyalty_points = total_loyalty_points + ?,
                    last_purchase_date = ?
                WHERE customer_id = ?
            """, (total_points_earned, txn_date, customer_id))
            
            total_points_updated += 1
        
        # Mark transaction as processed
        cursor.execute("""
            UPDATE staging_store_sales_header
            SET processed = 1
            WHERE transaction_id = ?
        """, (txn_id,))
    
    conn.commit()
    conn.close()
    
    print(f"[OK] Processed {total_points_updated} transactions and updated loyalty points")
    return total_points_updated

def execute(db_path):
    """Execute Use Case 3 pipeline"""
    print("\n" + "="*60)
    print("USE CASE 3: LOYALTY POINT CALCULATION ENGINE")
    print("="*60)
    
    count = calculate_loyalty_points(db_path)
    print(f"\n[OK] Use Case 3 completed successfully - {count} transactions processed")
    return count

