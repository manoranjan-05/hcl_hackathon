"""Use Case 4: Customer Segmentation for Targeted Offers"""
import sqlite3
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import get_connection

def calculate_rfm_metrics(db_path):
    """Calculate RFM metrics and segment customers"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear previous segments
    cursor.execute("DELETE FROM customer_segments")
    
    # Get current date (use max transaction date as reference)
    cursor.execute("SELECT MAX(transaction_date) FROM staging_store_sales_header")
    max_date_str = cursor.fetchone()[0]
    
    if max_date_str:
        try:
            max_date = datetime.strptime(max_date_str.split()[0], '%Y-%m-%d')
        except:
            max_date = datetime.now()
    else:
        max_date = datetime.now()
    
    # Calculate RFM metrics for each customer
    cursor.execute("""
        SELECT 
            c.customer_id,
            c.total_loyalty_points,
            COALESCE(MAX(h.transaction_date), c.last_purchase_date) as last_purchase,
            COUNT(DISTINCT h.transaction_id) as frequency,
            COALESCE(SUM(h.total_amount), 0) as monetary_value
        FROM staging_customer_details c
        LEFT JOIN staging_store_sales_header h ON c.customer_id = h.customer_id
        GROUP BY c.customer_id, c.total_loyalty_points, c.last_purchase_date
    """)
    
    customers = cursor.fetchall()
    
    # Calculate recency for each customer
    customer_data = []
    for cust_id, loyalty_points, last_purchase, frequency, monetary in customers:
        if last_purchase:
            try:
                last_purchase_date = datetime.strptime(last_purchase.split()[0], '%Y-%m-%d')
                recency_days = (max_date - last_purchase_date).days
            except:
                recency_days = 999
        else:
            recency_days = 999
        
        customer_data.append({
            'customer_id': cust_id,
            'recency_days': recency_days,
            'frequency': frequency or 0,
            'monetary_value': monetary or 0,
            'loyalty_points': loyalty_points or 0
        })
    
    # Calculate percentiles for segmentation
    monetary_values = [c['monetary_value'] for c in customer_data]
    monetary_values.sort(reverse=True)
    
    if monetary_values:
        top_10_percent_threshold = monetary_values[int(len(monetary_values) * 0.1)]
    else:
        top_10_percent_threshold = 0
    
    # Segment customers
    for customer in customer_data:
        segment_name = None
        
        # High-Spenders: Top 10% by monetary value
        if customer['monetary_value'] >= top_10_percent_threshold:
            segment_name = 'High-Spenders'
        
        # At-Risk: Haven't shopped in 60+ days but have points
        elif customer['recency_days'] >= 60 and customer['loyalty_points'] > 0:
            segment_name = 'At-Risk'
        
        # Regular customers (others)
        else:
            segment_name = 'Regular'
        
        # Insert segment
        cursor.execute("""
            INSERT INTO customer_segments
            (customer_id, segment_name, recency_days, frequency, monetary_value, loyalty_points)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            customer['customer_id'],
            segment_name,
            customer['recency_days'],
            customer['frequency'],
            customer['monetary_value'],
            customer['loyalty_points']
        ))
    
    # Update customer_details with segment_id
    cursor.execute("""
        UPDATE staging_customer_details
        SET segment_id = (
            SELECT segment_name
            FROM customer_segments
            WHERE customer_segments.customer_id = staging_customer_details.customer_id
        )
    """)
    
    # Get segment statistics
    cursor.execute("""
        SELECT segment_name, COUNT(*) as count
        FROM customer_segments
        GROUP BY segment_name
        ORDER BY count DESC
    """)
    
    segments = cursor.fetchall()
    
    conn.commit()
    conn.close()
    
    print("[OK] Customer segmentation complete")
    print("\nCustomer Segments:")
    print("-" * 40)
    for segment_name, count in segments:
        print(f"  {segment_name}: {count} customers")
    
    return segments

def execute(db_path):
    """Execute Use Case 4 pipeline"""
    print("\n" + "="*60)
    print("USE CASE 4: CUSTOMER SEGMENTATION FOR TARGETED OFFERS")
    print("="*60)
    
    segments = calculate_rfm_metrics(db_path)
    print("\n[OK] Use Case 4 completed successfully")
    return segments

