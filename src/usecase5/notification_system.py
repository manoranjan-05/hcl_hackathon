"""Use Case 5: Automated Loyalty Notification System"""
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import get_connection

def generate_notifications(db_path):
    """Generate and send loyalty point notifications"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear previous notifications
    cursor.execute("DELETE FROM loyalty_notifications")
    
    # Get customers with updated loyalty points (from recent transactions)
    cursor.execute("""
        SELECT DISTINCT
            lpt.customer_id,
            c.email,
            c.first_name,
            lpt.points_earned,
            c.total_loyalty_points
        FROM loyalty_point_transactions lpt
        JOIN staging_customer_details c ON lpt.customer_id = c.customer_id
        WHERE lpt.customer_id NOT IN (
            SELECT customer_id FROM loyalty_notifications 
            WHERE status = 'sent'
        )
    """)
    
    customers = cursor.fetchall()
    
    notifications_sent = 0
    
    for customer_id, email, first_name, points_earned, total_points in customers:
        # Generate email content
        subject = "Your Loyalty Points Update"
        body = f"""
Hi {first_name or 'Valued Customer'},

Great news! You've earned {points_earned} loyalty points from your recent purchase!

Your total loyalty points balance is now: {total_points} points

Thank you for being a loyal customer!

Best regards,
Retail Team
        """.strip()
        
        # Insert notification
        cursor.execute("""
            INSERT INTO loyalty_notifications
            (customer_id, email, subject, body, points_earned, total_points, status)
            VALUES (?, ?, ?, ?, ?, ?, 'sent')
        """, (customer_id, email, subject, body, points_earned, total_points))
        
        notifications_sent += 1
        
        # In a real system, this would send the email
        # For simulation, we just log it
        print(f"[NOTIFICATION] Sent to {email}: Earned {points_earned} points, Total: {total_points}")
    
    conn.commit()
    conn.close()
    
    print(f"\n[OK] Generated {notifications_sent} loyalty notifications")
    return notifications_sent

def execute(db_path):
    """Execute Use Case 5 pipeline"""
    print("\n" + "="*60)
    print("USE CASE 5: AUTOMATED LOYALTY NOTIFICATION SYSTEM")
    print("="*60)
    
    count = generate_notifications(db_path)
    print(f"\n[OK] Use Case 5 completed successfully - {count} notifications sent")
    return count

