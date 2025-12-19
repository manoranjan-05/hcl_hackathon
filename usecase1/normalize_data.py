"""Normalize denormalized data during ingestion"""
import sqlite3
import pandas as pd

def normalize_1nf(db_path='retail_db.sqlite'):
    """Normalize to 1NF: Split multi-value cells, remove repeating groups"""
    conn = sqlite3.connect(db_path)
    
    # Load line items data
    df = pd.read_sql("SELECT * FROM raw_store_sales_line_items", conn)
    
    # Find rows with comma-separated product_ids (1NF violation)
    split_rows = []
    rows_to_remove = []
    
    max_id = df['line_item_id'].max() if len(df) > 0 else 0
    new_id = int(max_id) + 1
    
    for idx, row in df.iterrows():
        product_id = str(row['product_id']) if pd.notna(row['product_id']) else ''
        if ',' in product_id:
            # Split into multiple rows
            product_ids = [p.strip().strip('"') for p in product_id.split(',')]
            for i, pid in enumerate(product_ids):
                if pid:  # Only if not empty
                    new_row = row.copy()
                    new_row['line_item_id'] = new_id if i == 0 else new_id + i
                    new_row['product_id'] = pid
                    # Adjust line_item_amount proportionally
                    new_row['line_item_amount'] = row['line_item_amount'] / len(product_ids)
                    split_rows.append(new_row)
            new_id += len(product_ids)
            rows_to_remove.append(idx)
    
    if split_rows:
        # Remove original rows with commas
        df_clean = df.drop(rows_to_remove)
        # Add split rows
        split_df = pd.DataFrame(split_rows)
        df_final = pd.concat([df_clean, split_df], ignore_index=True)
        df_final.to_sql('raw_store_sales_line_items', conn, if_exists='replace', index=False)
        print(f"[OK] 1NF: Split {len(split_rows)} multi-value product_id records")
    
    conn.commit()
    conn.close()

def normalize_2nf(db_path='retail_db.sqlite'):
    """Normalize to 2NF: Remove partial dependencies (product_name, product_category)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if partial dependency columns exist
    cursor.execute("PRAGMA table_info(raw_store_sales_line_items)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Remove product-related columns that should be in products table (2NF violation)
    partial_dep_cols = ['product_name', 'product_category', 'unit_price']
    cols_to_remove = [col for col in partial_dep_cols if col in columns]
    
    if cols_to_remove:
        # Keep only columns that fully depend on primary key
        keep_cols = ['line_item_id', 'transaction_id', 'product_id', 'promotion_id', 'quantity', 'line_item_amount']
        # Add load_timestamp if it exists
        if 'load_timestamp' in columns:
            keep_cols.append('load_timestamp')
        
        cursor.execute(f"""
            CREATE TABLE temp_line_items AS 
            SELECT {', '.join(keep_cols)}
            FROM raw_store_sales_line_items
        """)
        cursor.execute("DROP TABLE raw_store_sales_line_items")
        cursor.execute("ALTER TABLE temp_line_items RENAME TO raw_store_sales_line_items")
        print(f"[OK] 2NF: Removed partial dependency columns: {', '.join(cols_to_remove)}")
    
    conn.commit()
    conn.close()

def normalize_3nf(db_path='retail_db.sqlite'):
    """Normalize to 3NF: Remove transitive dependencies (store_city, store_region)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if transitive dependency columns exist
    cursor.execute("PRAGMA table_info(raw_store_sales_header)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Remove transitive dependency columns (3NF violation)
    transitive_cols = ['store_city', 'store_region', 'customer_name', 'customer_email']
    cols_to_remove = [col for col in transitive_cols if col in columns]
    
    if cols_to_remove:
        # Keep only columns that directly depend on primary key
        keep_cols = ['transaction_id', 'customer_id', 'store_id', 'transaction_date', 'total_amount']
        # Add load_timestamp if it exists
        if 'load_timestamp' in columns:
            keep_cols.append('load_timestamp')
        
        cursor.execute(f"""
            CREATE TABLE temp_header AS 
            SELECT {', '.join(keep_cols)}
            FROM raw_store_sales_header
        """)
        cursor.execute("DROP TABLE raw_store_sales_header")
        cursor.execute("ALTER TABLE temp_header RENAME TO raw_store_sales_header")
        print(f"[OK] 3NF: Removed transitive dependency columns: {', '.join(cols_to_remove)}")
    
    conn.commit()
    conn.close()

def normalize_all(db_path='retail_db.sqlite'):
    """Apply all normalization steps"""
    print("\n[Normalization] Applying normalization rules...")
    normalize_1nf(db_path)
    normalize_2nf(db_path)
    normalize_3nf(db_path)
    print("[OK] Normalization complete")

