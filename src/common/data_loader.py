"""Data loading utilities"""
import sqlite3
import pandas as pd
import os

def get_data_dir():
    """Get data directory path"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, 'data')

def load_master_data(db_path):
    """Load master data tables"""
    conn = sqlite3.connect(db_path)
    data_dir = get_data_dir()
    
    tables = ['stores', 'products', 'customer_details', 'promotion_details', 'loyalty_rules']
    for table in tables:
        csv_path = os.path.join(data_dir, f'{table}.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.to_sql(f'staging_{table}', conn, if_exists='replace', index=False)
            print(f"[OK] Loaded {table}: {len(df)} records")
        else:
            print(f"[WARN] File not found: {csv_path}")
    
    conn.close()

def load_raw_sales_data(db_path):
    """Load raw sales data"""
    conn = sqlite3.connect(db_path)
    data_dir = get_data_dir()
    
    # Load header data
    header_path = os.path.join(data_dir, 'store_sales_header.csv')
    if os.path.exists(header_path):
        header_df = pd.read_csv(header_path)
        header_df.to_sql('raw_store_sales_header', conn, if_exists='replace', index=False)
        print(f"[OK] Loaded header: {len(header_df)} records")
    
    # Load line items data
    line_items_path = os.path.join(data_dir, 'store_sales_line_items.csv')
    if os.path.exists(line_items_path):
        line_items_df = pd.read_csv(line_items_path)
        line_items_df.to_sql('raw_store_sales_line_items', conn, if_exists='replace', index=False)
        print(f"[OK] Loaded line items: {len(line_items_df)} records")
    
    conn.close()

