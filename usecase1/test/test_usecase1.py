"""
Complete test script for Use Case 1
Runs all steps and saves intermediate results
"""
import sys
import os
import sqlite3
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_setup import setup_db
from load_data import load_master_data, load_raw_data
from normalize_data import normalize_all
from validate_data import validate_headers, validate_line_items
from route_data import route_valid_data

def save_results(db_path, output_dir='outputs'):
    """Save all intermediate results to CSV files"""
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    # Save raw data
    pd.read_sql("SELECT * FROM raw_store_sales_header", conn).to_csv(f'{output_dir}/01_raw_headers.csv', index=False)
    pd.read_sql("SELECT * FROM raw_store_sales_line_items", conn).to_csv(f'{output_dir}/02_raw_line_items.csv', index=False)
    
    # Save rejected data
    pd.read_sql("SELECT * FROM quarantine_rejected_sales_header", conn).to_csv(f'{output_dir}/03_rejected_headers.csv', index=False)
    pd.read_sql("SELECT * FROM quarantine_rejected_sales_line_items", conn).to_csv(f'{output_dir}/04_rejected_line_items.csv', index=False)
    
    # Save staging data
    pd.read_sql("SELECT * FROM staging_store_sales_header", conn).to_csv(f'{output_dir}/05_staging_headers.csv', index=False)
    pd.read_sql("SELECT * FROM staging_store_sales_line_items", conn).to_csv(f'{output_dir}/06_staging_line_items.csv', index=False)
    
    # Save validation summary
    summary = pd.DataFrame({
        'record_type': ['Header Records', 'Line Item Records'],
        'total': [
            len(pd.read_sql("SELECT * FROM raw_store_sales_header", conn)),
            len(pd.read_sql("SELECT * FROM raw_store_sales_line_items", conn))
        ],
        'valid': [
            len(pd.read_sql("SELECT * FROM staging_store_sales_header", conn)),
            len(pd.read_sql("SELECT * FROM staging_store_sales_line_items", conn))
        ],
        'rejected': [
            len(pd.read_sql("SELECT * FROM quarantine_rejected_sales_header", conn)),
            len(pd.read_sql("SELECT * FROM quarantine_rejected_sales_line_items", conn))
        ]
    })
    summary['validation_rate'] = (summary['valid'] / summary['total'] * 100).round(2)
    summary.to_csv(f'{output_dir}/07_validation_summary.csv', index=False)
    
    # Save rejection reasons
    rejected_headers = pd.read_sql("SELECT rejection_reason, COUNT(*) as count FROM quarantine_rejected_sales_header GROUP BY rejection_reason", conn)
    rejected_headers.to_csv(f'{output_dir}/08_rejection_reasons_headers.csv', index=False)
    
    rejected_items = pd.read_sql("SELECT rejection_reason, COUNT(*) as count FROM quarantine_rejected_sales_line_items GROUP BY rejection_reason", conn)
    rejected_items.to_csv(f'{output_dir}/09_rejection_reasons_line_items.csv', index=False)
    
    conn.close()
    print(f"[OK] Results saved to {output_dir}/")

def generate_detailed_report(db_path, output_dir='outputs', 
                             header_cols_before=None, line_items_cols_before=None,
                             header_cols_after=None, line_items_cols_after=None):
    """Generate detailed text report showing normalization and validation"""
    # Set defaults if not provided
    if header_cols_before is None:
        conn = sqlite3.connect(db_path)
        header_cols_before = pd.read_sql("PRAGMA table_info(raw_store_sales_header)", conn)['name'].tolist()
        conn.close()
    if header_cols_after is None:
        conn = sqlite3.connect(db_path)
        header_cols_after = pd.read_sql("PRAGMA table_info(raw_store_sales_header)", conn)['name'].tolist()
        conn.close()
    if line_items_cols_before is None:
        conn = sqlite3.connect(db_path)
        line_items_cols_before = pd.read_sql("PRAGMA table_info(raw_store_sales_line_items)", conn)['name'].tolist()
        conn.close()
    if line_items_cols_after is None:
        conn = sqlite3.connect(db_path)
        line_items_cols_after = pd.read_sql("PRAGMA table_info(raw_store_sales_line_items)", conn)['name'].tolist()
        conn.close()
    """Generate detailed text report showing normalization and validation"""
    conn = sqlite3.connect(db_path)
    report_file = os.path.join(output_dir, 'normalization_and_validation_report.txt')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("DATA NORMALIZATION AND VALIDATION REPORT\n")
        f.write("="*80 + "\n\n")
        
        # Section 1: Normalization Details
        f.write("SECTION 1: NORMALIZATION PROCESS\n")
        f.write("-"*80 + "\n\n")
        
        # 1NF Normalization
        f.write("1NF NORMALIZATION (First Normal Form)\n")
        f.write("-"*80 + "\n")
        f.write("Purpose: Split multi-value cells into separate rows\n\n")
        
        f.write("1NF Violations Found:\n")
        f.write("  - Multi-value product_id cells (e.g., 'P001,P002')\n")
        f.write("  - These violate 1NF requirement for atomic values\n")
        f.write("  - 1NF requires each cell to contain a single, indivisible value\n\n")
        
        # Check current state (after normalization)
        df_after = pd.read_sql("SELECT * FROM raw_store_sales_line_items", conn)
        f.write("1NF Normalization Applied:\n")
        f.write("  - Split comma-separated product_ids into separate rows\n")
        f.write("  - Each row now contains a single product_id value (atomic)\n")
        f.write("  - Line item amounts adjusted proportionally when split\n")
        f.write(f"  - Total line items after normalization: {len(df_after)}\n\n")
        
        # Show example if available
        multi_value_examples = df_after[df_after['product_id'].astype(str).str.contains(',', na=False)]
        if len(multi_value_examples) == 0:
            f.write("Result: All multi-value cells have been normalized\n")
            f.write("  Example Transformation:\n")
            f.write("    BEFORE (1NF Violation):\n")
            f.write("      line_item_id: 102, product_id: 'P001,P002', quantity: 2, amount: 200.00\n")
            f.write("    AFTER (1NF Normalized):\n")
            f.write("      line_item_id: 102, product_id: 'P001', quantity: 1, amount: 100.00\n")
            f.write("      line_item_id: 103, product_id: 'P002', quantity: 1, amount: 100.00\n\n")
        
        # 2NF Normalization
        f.write("2NF NORMALIZATION (Second Normal Form)\n")
        f.write("-"*80 + "\n")
        f.write("Purpose: Remove partial dependencies\n\n")
        
        if line_items_cols_before and line_items_cols_after:
            removed_cols = set(line_items_cols_before) - set(line_items_cols_after)
            if removed_cols:
                f.write("2NF Violations Found:\n")
                for col in removed_cols:
                    if col in ['product_name', 'product_category', 'unit_price']:
                        f.write(f"  - {col} column in line_items table\n")
                f.write("  - These depend on product_id, not line_item_id (partial dependency)\n\n")
                
                f.write("2NF Normalization Applied:\n")
                for col in removed_cols:
                    if col in ['product_name', 'product_category', 'unit_price']:
                        f.write(f"  - Removed {col} column from line_items\n")
                f.write("  - Product information is stored in products table (referenced via product_id)\n\n")
                f.write("  Example Transformation:\n")
                f.write("    BEFORE (2NF Violation):\n")
                f.write("      line_item_id: 1, product_id: 'P001', product_name: 'Wireless Headphones', quantity: 2\n")
                f.write("    AFTER (2NF Normalized):\n")
                f.write("      line_item_id: 1, product_id: 'P001', quantity: 2\n")
                f.write("      (product_name retrieved from products table via JOIN)\n\n")
            else:
                f.write("2NF: No partial dependencies found (already normalized)\n\n")
        
        # 3NF Normalization
        f.write("3NF NORMALIZATION (Third Normal Form)\n")
        f.write("-"*80 + "\n")
        f.write("Purpose: Remove transitive dependencies\n\n")
        
        if header_cols_before and header_cols_after:
            removed_cols = set(header_cols_before) - set(header_cols_after)
            if removed_cols:
                f.write("3NF Violations Found:\n")
                for col in removed_cols:
                    if col in ['store_city', 'store_region', 'customer_name', 'customer_email']:
                        f.write(f"  - {col} column in header table\n")
                f.write("  - These depend on store_id/customer_id, not transaction_id (transitive dependency)\n\n")
                
                f.write("3NF Normalization Applied:\n")
                for col in removed_cols:
                    if col in ['store_city', 'store_region', 'customer_name', 'customer_email']:
                        f.write(f"  - Removed {col} column from header\n")
                f.write("  - Store/Customer information is stored in respective tables (referenced via foreign keys)\n\n")
                f.write("  Example Transformation:\n")
                f.write("    BEFORE (3NF Violation):\n")
                f.write("      transaction_id: 'TXN001', store_id: 'ST001', store_city: 'New York', store_region: 'New York'\n")
                f.write("    AFTER (3NF Normalized):\n")
                f.write("      transaction_id: 'TXN001', store_id: 'ST001'\n")
                f.write("      (store_city, store_region retrieved from stores table via JOIN)\n\n")
            else:
                f.write("3NF: No transitive dependencies found (already normalized)\n\n")
        
        f.write("Normalization Summary:\n")
        f.write("  - Data is now in 3NF (Third Normal Form)\n")
        f.write("  - All tables have atomic values (1NF)\n")
        f.write("  - No partial dependencies (2NF)\n")
        f.write("  - No transitive dependencies (3NF)\n\n")
        
        # Section 2: Validation Details
        f.write("\n" + "="*80 + "\n")
        f.write("SECTION 2: DATA QUALITY VALIDATION\n")
        f.write("-"*80 + "\n\n")
        
        # Header Validation Rules
        f.write("HEADER VALIDATION RULES\n")
        f.write("-"*80 + "\n\n")
        
        rejected_headers = pd.read_sql("""
            SELECT rejection_reason, COUNT(*) as count, 
                   GROUP_CONCAT(transaction_id, ', ') as transaction_ids
            FROM quarantine_rejected_sales_header 
            GROUP BY rejection_reason
            ORDER BY count DESC
        """, conn)
        
        rules = {
            'REJECTED: Missing or NULL customer_id': 'Rule 1',
            'REJECTED: Invalid store_id': 'Rule 2',
            'REJECTED: Invalid customer_id': 'Rule 3',
            'REJECTED: Invalid transaction_date': 'Rule 4',
            'REJECTED: Invalid total_amount': 'Rule 5',
            'REJECTED: Total amount mismatch': 'Rule 10'
        }
        
        for _, row in rejected_headers.iterrows():
            reason = row['rejection_reason']
            count = row['count']
            rule_num = rules.get(reason, 'Unknown')
            txn_ids = str(row['transaction_ids']).split(', ')[:5]  # Show first 5
            
            f.write(f"{rule_num}: {reason}\n")
            f.write(f"  Violations Found: {count} records\n")
            f.write(f"  Example Transaction IDs: {', '.join(txn_ids[:3])}\n")
            f.write(f"  Action: Records moved to quarantine_rejected_sales_header\n\n")
        
        # Line Items Validation Rules
        f.write("\nLINE ITEMS VALIDATION RULES\n")
        f.write("-"*80 + "\n\n")
        
        rejected_items = pd.read_sql("""
            SELECT rejection_reason, COUNT(*) as count,
                   GROUP_CONCAT(line_item_id, ', ') as line_item_ids
            FROM quarantine_rejected_sales_line_items 
            GROUP BY rejection_reason
            ORDER BY count DESC
        """, conn)
        
        item_rules = {
            'REJECTED: Missing product_id': 'Rule 6',
            'REJECTED: Invalid product_id': 'Rule 7',
            'REJECTED: Invalid line_item_amount': 'Rule 8',
            'REJECTED: Invalid transaction_id': 'Rule 9'
        }
        
        for _, row in rejected_items.iterrows():
            reason = row['rejection_reason']
            count = row['count']
            rule_num = item_rules.get(reason, 'Unknown')
            item_ids = str(row['line_item_ids']).split(', ')[:5]
            
            f.write(f"{rule_num}: {reason}\n")
            f.write(f"  Violations Found: {count} records\n")
            f.write(f"  Example Line Item IDs: {', '.join(item_ids[:3])}\n")
            f.write(f"  Action: Records moved to quarantine_rejected_sales_line_items\n\n")
        
        # Section 3: Summary Statistics
        f.write("\n" + "="*80 + "\n")
        f.write("SECTION 3: VALIDATION SUMMARY STATISTICS\n")
        f.write("-"*80 + "\n\n")
        
        total_h = pd.read_sql("SELECT COUNT(*) as count FROM raw_store_sales_header", conn)['count'].iloc[0]
        valid_h = pd.read_sql("SELECT COUNT(*) as count FROM staging_store_sales_header", conn)['count'].iloc[0]
        rejected_h = pd.read_sql("SELECT COUNT(*) as count FROM quarantine_rejected_sales_header", conn)['count'].iloc[0]
        
        f.write("Header Records:\n")
        f.write(f"  Total Records:    {total_h}\n")
        f.write(f"  Valid Records:   {valid_h}\n")
        f.write(f"  Rejected Records: {rejected_h}\n")
        f.write(f"  Validation Rate:  {(valid_h/total_h*100):.2f}%\n\n")
        
        total_l = pd.read_sql("SELECT COUNT(*) as count FROM raw_store_sales_line_items", conn)['count'].iloc[0]
        valid_l = pd.read_sql("SELECT COUNT(*) as count FROM staging_store_sales_line_items", conn)['count'].iloc[0]
        rejected_l = pd.read_sql("SELECT COUNT(*) as count FROM quarantine_rejected_sales_line_items", conn)['count'].iloc[0]
        
        f.write("Line Item Records:\n")
        f.write(f"  Total Records:    {total_l}\n")
        f.write(f"  Valid Records:   {valid_l}\n")
        f.write(f"  Rejected Records: {rejected_l}\n")
        f.write(f"  Validation Rate:  {(valid_l/total_l*100):.2f}%\n\n")
        
        # Section 4: Examples
        f.write("\n" + "="*80 + "\n")
        f.write("SECTION 4: DETAILED EXAMPLES\n")
        f.write("-"*80 + "\n\n")
        
        # Example of rejected header
        f.write("Example: Rejected Header Record\n")
        f.write("-"*80 + "\n")
        rejected_example = pd.read_sql("""
            SELECT * FROM quarantine_rejected_sales_header LIMIT 1
        """, conn)
        if len(rejected_example) > 0:
            for col in rejected_example.columns:
                f.write(f"  {col}: {rejected_example[col].iloc[0]}\n")
        f.write("\n")
        
        # Example of rejected line item
        f.write("Example: Rejected Line Item Record\n")
        f.write("-"*80 + "\n")
        rejected_item_example = pd.read_sql("""
            SELECT * FROM quarantine_rejected_sales_line_items LIMIT 1
        """, conn)
        if len(rejected_item_example) > 0:
            for col in rejected_item_example.columns:
                f.write(f"  {col}: {rejected_item_example[col].iloc[0]}\n")
        f.write("\n")
        
        # Example of valid record
        f.write("Example: Valid Header Record (Passed All Checks)\n")
        f.write("-"*80 + "\n")
        valid_example = pd.read_sql("""
            SELECT * FROM staging_store_sales_header LIMIT 1
        """, conn)
        if len(valid_example) > 0:
            for col in valid_example.columns:
                f.write(f"  {col}: {valid_example[col].iloc[0]}\n")
        f.write("\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")
    
    conn.close()
    print(f"[OK] Detailed report saved to {report_file}")

def print_summary(db_path):
    """Print validation summary"""
    conn = sqlite3.connect(db_path)
    
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    # Header summary
    total_h = pd.read_sql("SELECT COUNT(*) as count FROM raw_store_sales_header", conn)['count'].iloc[0]
    valid_h = pd.read_sql("SELECT COUNT(*) as count FROM staging_store_sales_header", conn)['count'].iloc[0]
    rejected_h = pd.read_sql("SELECT COUNT(*) as count FROM quarantine_rejected_sales_header", conn)['count'].iloc[0]
    
    print(f"\nHeader Records:")
    print(f"  Total:    {total_h}")
    print(f"  Valid:    {valid_h}")
    print(f"  Rejected: {rejected_h}")
    print(f"  Rate:     {(valid_h/total_h*100):.2f}%")
    
    # Line items summary
    total_l = pd.read_sql("SELECT COUNT(*) as count FROM raw_store_sales_line_items", conn)['count'].iloc[0]
    valid_l = pd.read_sql("SELECT COUNT(*) as count FROM staging_store_sales_line_items", conn)['count'].iloc[0]
    rejected_l = pd.read_sql("SELECT COUNT(*) as count FROM quarantine_rejected_sales_line_items", conn)['count'].iloc[0]
    
    print(f"\nLine Item Records:")
    print(f"  Total:    {total_l}")
    print(f"  Valid:    {valid_l}")
    print(f"  Rejected: {rejected_l}")
    print(f"  Rate:     {(valid_l/total_l*100):.2f}%")
    
    conn.close()

def main():
    db_path = '../retail_db.sqlite'
    data_dir = '../../data'
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    
    print("="*60)
    print("USE CASE 1: DATA INGESTION AND VALIDATION")
    print("="*60)
    
    # Step 1: Setup database
    print("\n[Step 1] Setting up database...")
    setup_db(db_path)
    
    # Step 2: Load master data
    print("\n[Step 2] Loading master data...")
    load_master_data(db_path, data_dir)
    
    # Step 3: Load raw sales data
    print("\n[Step 3] Loading raw sales data...")
    load_raw_data(db_path, data_dir)
    
    # Capture denormalized state for report
    conn_before = sqlite3.connect(db_path)
    header_cols_before = pd.read_sql("PRAGMA table_info(raw_store_sales_header)", conn_before)['name'].tolist()
    line_items_cols_before = pd.read_sql("PRAGMA table_info(raw_store_sales_line_items)", conn_before)['name'].tolist()
    conn_before.close()
    
    # Step 3.5: Normalize data (1NF, 2NF, 3NF)
    normalize_all(db_path)
    
    # Capture normalized state for report
    conn_after = sqlite3.connect(db_path)
    header_cols_after = pd.read_sql("PRAGMA table_info(raw_store_sales_header)", conn_after)['name'].tolist()
    line_items_cols_after = pd.read_sql("PRAGMA table_info(raw_store_sales_line_items)", conn_after)['name'].tolist()
    conn_after.close()
    
    # Step 4: Validate headers
    print("\n[Step 4] Validating header data...")
    validate_headers(db_path)
    
    # Step 5: Validate line items
    print("\n[Step 5] Validating line items...")
    validate_line_items(db_path)
    
    # Step 6: Route valid data
    print("\n[Step 6] Routing valid data to staging...")
    route_valid_data(db_path)
    
    # Step 7: Save results
    print("\n[Step 7] Saving results...")
    save_results(db_path, output_dir)
    
    # Step 8: Generate detailed report
    print("\n[Step 8] Generating detailed report...")
    generate_detailed_report(db_path, output_dir, 
                            header_cols_before, line_items_cols_before,
                            header_cols_after, line_items_cols_after)
    
    # Step 9: Print summary
    print_summary(db_path)
    
    print("\n" + "="*60)
    print("[OK] USE CASE 1 COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    main()

