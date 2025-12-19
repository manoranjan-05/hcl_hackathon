# Data Loading Code Snippets

Simple Python code to load CSV data into database tables.

---

## Prerequisites

Install required packages:

```bash
pip install pandas sqlalchemy psycopg2-binary  # For PostgreSQL
# OR
pip install pandas sqlalchemy pymysql          # For MySQL
```

---

## Step 1: Database Connection Setup

### PostgreSQL Connection

```python
from sqlalchemy import create_engine
import pandas as pd

# Database connection string
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'retail_db',
    'user': 'your_username',
    'password': 'your_password'
}

# Create connection
connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)
```

### MySQL Connection

```python
from sqlalchemy import create_engine
import pandas as pd

# Database connection string
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'retail_db',
    'user': 'your_username',
    'password': 'your_password'
}

# Create connection
connection_string = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)
```

---

## Step 2: Create Schemas

```python
from sqlalchemy import text

def create_schemas(engine):
    """Create raw, staging, and quarantine schemas"""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS quarantine"))
        conn.commit()
    print("Schemas created successfully!")

# Execute
create_schemas(engine)
```

---

## Step 3: Load Master Data to Staging

```python
def load_master_data(engine):
    """Load master data CSV files into staging schema"""
    
    master_tables = {
        'stores': 'data/stores.csv',
        'products': 'data/products.csv',
        'customer_details': 'data/customer_details.csv',
        'promotion_details': 'data/promotion_details.csv',
        'loyalty_rules': 'data/loyalty_rules.csv'
    }
    
    for table_name, file_path in master_tables.items():
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Load to database
        df.to_sql(
            name=table_name,
            con=engine,
            schema='staging',
            if_exists='replace',  # Use 'append' for incremental loads
            index=False
        )
        print(f"✓ Loaded {table_name}: {len(df)} records")

# Execute
load_master_data(engine)
```

---

## Step 4: Load Raw Sales Data

```python
def load_raw_sales_data(engine):
    """Load sales CSV files into raw schema"""
    
    # Load header data
    header_df = pd.read_csv('data/store_sales_header.csv')
    header_df.to_sql(
        name='store_sales_header',
        con=engine,
        schema='raw',
        if_exists='replace',
        index=False
    )
    print(f"✓ Loaded store_sales_header: {len(header_df)} records")
    
    # Load line items data
    line_items_df = pd.read_csv('data/store_sales_line_items.csv')
    line_items_df.to_sql(
        name='store_sales_line_items',
        con=engine,
        schema='raw',
        if_exists='replace',
        index=False
    )
    print(f"✓ Loaded store_sales_line_items: {len(line_items_df)} records")

# Execute
load_raw_sales_data(engine)
```

---

## Step 5: Complete Data Loading Script

Complete script combining all steps:

```python
from sqlalchemy import create_engine, text
import pandas as pd

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,  # 3306 for MySQL
    'database': 'retail_db',
    'user': 'your_username',
    'password': 'your_password'
}

# Create connection (PostgreSQL)
connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string)

def setup_database(engine):
    """Complete database setup and data loading"""
    
    # Step 1: Create schemas
    print("Creating schemas...")
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS quarantine"))
        conn.commit()
    print("✓ Schemas created")
    
    # Step 2: Load master data
    print("\nLoading master data...")
    master_tables = {
        'stores': 'data/stores.csv',
        'products': 'data/products.csv',
        'customer_details': 'data/customer_details.csv',
        'promotion_details': 'data/promotion_details.csv',
        'loyalty_rules': 'data/loyalty_rules.csv'
    }
    
    for table_name, file_path in master_tables.items():
        df = pd.read_csv(file_path)
        df.to_sql(
            name=table_name,
            con=engine,
            schema='staging',
            if_exists='replace',
            index=False
        )
        print(f"  ✓ {table_name}: {len(df)} records")
    
    # Step 3: Load raw sales data
    print("\nLoading raw sales data...")
    header_df = pd.read_csv('data/store_sales_header.csv')
    header_df.to_sql(
        name='store_sales_header',
        con=engine,
        schema='raw',
        if_exists='replace',
        index=False
    )
    print(f"  ✓ store_sales_header: {len(header_df)} records")
    
    line_items_df = pd.read_csv('data/store_sales_line_items.csv')
    line_items_df.to_sql(
        name='store_sales_line_items',
        con=engine,
        schema='raw',
        if_exists='replace',
        index=False
    )
    print(f"  ✓ store_sales_line_items: {len(line_items_df)} records")
    
    print("\n✓ Data loading completed!")

# Execute
if __name__ == "__main__":
    setup_database(engine)
```

---

## Step 6: Verify Data Loaded

```python
def verify_data_loaded(engine):
    """Verify data was loaded correctly"""
    
    tables = {
        'staging': ['stores', 'products', 'customer_details', 'promotion_details', 'loyalty_rules'],
        'raw': ['store_sales_header', 'store_sales_line_items']
    }
    
    print("Verifying data load...\n")
    for schema, table_list in tables.items():
        print(f"{schema.upper()} Schema:")
        for table in table_list:
            query = f"SELECT COUNT(*) as count FROM {schema}.{table}"
            result = pd.read_sql(query, engine)
            count = result['count'].iloc[0]
            print(f"  {table}: {count} records")
        print()

# Execute
verify_data_loaded(engine)
```

---

## Step 7: Handle Data Types (Optional)

If you need to specify data types explicitly:

```python
from sqlalchemy import VARCHAR, INTEGER, DECIMAL, TIMESTAMP, BOOLEAN

def load_with_data_types(engine):
    """Load data with explicit data type mapping"""
    
    # Define data types for header table
    dtype_header = {
        'transaction_id': VARCHAR(30),
        'customer_id': VARCHAR(20),
        'store_id': VARCHAR(10),
        'transaction_date': TIMESTAMP,
        'total_amount': DECIMAL(10, 2)
    }
    
    header_df = pd.read_csv('data/store_sales_header.csv')
    header_df.to_sql(
        name='store_sales_header',
        con=engine,
        schema='raw',
        if_exists='replace',
        index=False,
        dtype=dtype_header
    )
    
    # Define data types for line items table
    dtype_line_items = {
        'line_item_id': INTEGER,
        'transaction_id': VARCHAR(30),
        'product_id': VARCHAR(20),
        'promotion_id': VARCHAR(10),
        'quantity': INTEGER,
        'line_item_amount': DECIMAL(10, 2)
    }
    
    line_items_df = pd.read_csv('data/store_sales_line_items.csv')
    line_items_df.to_sql(
        name='store_sales_line_items',
        con=engine,
        schema='raw',
        if_exists='replace',
        index=False,
        dtype=dtype_line_items
    )
```

---

## Step 8: Error Handling

```python
def safe_load_data(engine, table_name, file_path, schema='staging'):
    """Load data with error handling"""
    try:
        df = pd.read_csv(file_path)
        
        # Basic validation
        if df.empty:
            print(f"⚠ Warning: {file_path} is empty")
            return
        
        # Load to database
        df.to_sql(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists='replace',
            index=False
        )
        print(f"✓ Successfully loaded {table_name}: {len(df)} records")
        
    except FileNotFoundError:
        print(f"✗ Error: File {file_path} not found")
    except Exception as e:
        print(f"✗ Error loading {table_name}: {str(e)}")

# Usage
safe_load_data(engine, 'stores', 'data/stores.csv', 'staging')
```

---

## Quick Reference

### Load Single CSV File

```python
df = pd.read_csv('data/stores.csv')
df.to_sql('stores', engine, schema='staging', if_exists='replace', index=False)
```

### Load Multiple CSV Files

```python
files = {
    'stores': 'data/stores.csv',
    'products': 'data/products.csv'
}

for table, file in files.items():
    df = pd.read_csv(file)
    df.to_sql(table, engine, schema='staging', if_exists='replace', index=False)
```

### Check if Table Exists

```python
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names(schema='staging')
print(f"Tables in staging: {tables}")
```

---

## Notes

- Use `if_exists='replace'` to overwrite existing tables
- Use `if_exists='append'` to add data to existing tables
- Use `if_exists='fail'` to raise error if table exists
- Set `index=False` to avoid loading pandas index as a column
- For large files, consider chunking: `chunksize=1000` parameter

