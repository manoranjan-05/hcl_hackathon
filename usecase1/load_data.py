"""Load CSV data into database"""
import sqlite3
import pandas as pd
import os

def load_master_data(db_path='retail_db.sqlite', data_dir='../data'):
    conn = sqlite3.connect(db_path)
    
    tables = ['stores', 'products', 'customer_details', 'promotion_details', 'loyalty_rules']
    for table in tables:
        df = pd.read_csv(f'{data_dir}/{table}.csv')
        df.to_sql(f'staging_{table}', conn, if_exists='replace', index=False)
        print(f"[OK] Loaded {table}: {len(df)} records")
    
    conn.close()

def load_raw_data(db_path='retail_db.sqlite', data_dir='../data'):
    conn = sqlite3.connect(db_path)
    
    # Load header data (may contain denormalized columns like store_city, store_region)
    header_df = pd.read_csv(f'{data_dir}/store_sales_header.csv')
    header_df.to_sql('raw_store_sales_header', conn, if_exists='replace', index=False)
    print(f"[OK] Loaded header: {len(header_df)} records (may contain denormalized data)")
    
    # Load line items data (may contain denormalized columns like product_name, product_category)
    line_items_df = pd.read_csv(f'{data_dir}/store_sales_line_items.csv')
    line_items_df.to_sql('raw_store_sales_line_items', conn, if_exists='replace', index=False)
    print(f"[OK] Loaded line items: {len(line_items_df)} records (may contain denormalized data)")
    
    conn.close()

