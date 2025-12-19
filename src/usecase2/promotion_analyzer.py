"""Use Case 2: Real-Time Promotion Effectiveness Analyzer"""
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.database import get_connection

def calculate_promotion_effectiveness(db_path):
    """Calculate promotion effectiveness and rank top 3"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear previous results
    cursor.execute("DELETE FROM promotion_effectiveness")
    
    # Calculate baseline sales (non-promoted items) by category
    cursor.execute("""
        CREATE TEMP TABLE baseline_sales AS
        SELECT 
            p.product_category as category,
            SUM(li.quantity) as total_quantity,
            SUM(li.line_item_amount) as total_revenue,
            COUNT(DISTINCT li.product_id) as product_count
        FROM staging_store_sales_line_items li
        JOIN staging_products p ON li.product_id = p.product_id
        WHERE li.promotion_id IS NULL
        GROUP BY p.product_category
    """)
    
    # Calculate promoted sales by promotion and category
    cursor.execute("""
        CREATE TEMP TABLE promoted_sales AS
        SELECT 
            li.promotion_id,
            pd.promotion_name,
            p.product_category as category,
            SUM(li.quantity) as total_quantity,
            SUM(li.line_item_amount) as total_revenue
        FROM staging_store_sales_line_items li
        JOIN staging_products p ON li.product_id = p.product_id
        JOIN staging_promotion_details pd ON li.promotion_id = pd.promotion_id
        WHERE li.promotion_id IS NOT NULL
        GROUP BY li.promotion_id, pd.promotion_name, p.product_category
    """)
    
    # Calculate sales lift for each promotion
    cursor.execute("""
        INSERT INTO promotion_effectiveness 
        (promotion_id, promotion_name, category, baseline_sales, promoted_sales, sales_lift_percentage)
        SELECT 
            ps.promotion_id,
            ps.promotion_name,
            ps.category,
            COALESCE(bs.total_revenue, 0) as baseline_sales,
            ps.total_revenue as promoted_sales,
            CASE 
                WHEN COALESCE(bs.total_revenue, 0) > 0 
                THEN ((ps.total_revenue - COALESCE(bs.total_revenue, 0)) / bs.total_revenue) * 100
                ELSE 0
            END as sales_lift_percentage
        FROM promoted_sales ps
        LEFT JOIN baseline_sales bs ON ps.category = bs.category
    """)
    
    # Rank promotions by sales lift
    cursor.execute("""
        UPDATE promotion_effectiveness
        SET rank = (
            SELECT COUNT(*) + 1
            FROM promotion_effectiveness p2
            WHERE p2.sales_lift_percentage > promotion_effectiveness.sales_lift_percentage
        )
    """)
    
    # Get top 3 promotions
    cursor.execute("""
        SELECT promotion_id, promotion_name, category, baseline_sales, promoted_sales, 
               sales_lift_percentage, rank
        FROM promotion_effectiveness
        ORDER BY sales_lift_percentage DESC
        LIMIT 3
    """)
    
    top_promotions = cursor.fetchall()
    
    conn.commit()
    conn.close()
    
    print("[OK] Promotion effectiveness analysis complete")
    print("\nTop 3 Most Effective Promotions:")
    print("-" * 80)
    for promo in top_promotions:
        promo_id, name, category, baseline, promoted, lift, rank = promo
        print(f"Rank {rank}: {name} ({promo_id})")
        print(f"  Category: {category}")
        print(f"  Baseline Sales: ${baseline:.2f}")
        print(f"  Promoted Sales: ${promoted:.2f}")
        print(f"  Sales Lift: {lift:.2f}%")
        print()
    
    return top_promotions

def execute(db_path):
    """Execute Use Case 2 pipeline"""
    print("\n" + "="*60)
    print("USE CASE 2: REAL-TIME PROMOTION EFFECTIVENESS ANALYZER")
    print("="*60)
    
    results = calculate_promotion_effectiveness(db_path)
    print("\n[OK] Use Case 2 completed successfully")
    return results

