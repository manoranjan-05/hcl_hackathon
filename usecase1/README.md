# Use Case 1: Data Ingestion and Quality Validation

## Setup Instructions

### 1. Install Dependencies

```bash
cd usecase1
pip install -r requirements.txt
```

### 2. Setup SQLite Database

SQLite comes built-in with Python (no separate installation needed). Verify and create database:

```bash
python setup_sqlite.py
```

**What this does:**
- Checks if SQLite is available (it should be - comes with Python)
- Creates `retail_db.sqlite` database file in the current directory

**Note:** If SQLite is not available (rare), you may need to install Python with SQLite support or use a different Python distribution.

### 3. Run Complete Test

Run the complete test script that executes all steps:

```bash
cd test
python test_usecase1.py
```

This will:
1. Create database tables
2. Load master data (stores, products, customers, etc.)
3. Load raw sales data
4. Apply all validation rules
5. Route valid data to staging
6. Save all intermediate results to `outputs/` folder

## Output Files

All results are saved in `test/outputs/` folder:

- `01_raw_headers.csv` - Raw header data
- `02_raw_line_items.csv` - Raw line items data
- `03_rejected_headers.csv` - Rejected header records
- `04_rejected_line_items.csv` - Rejected line item records
- `05_staging_headers.csv` - Valid header records
- `06_staging_line_items.csv` - Valid line item records
- `07_validation_summary.csv` - Validation statistics
- `08_rejection_reasons_headers.csv` - Rejection reasons for headers
- `09_rejection_reasons_line_items.csv` - Rejection reasons for line items

## Project Structure

```
usecase1/
├── database_setup.py      # Create tables
├── load_data.py           # Load CSV data
├── validate_data.py        # Validation rules
├── route_data.py          # Route valid data
├── setup_sqlite.py        # SQLite setup
├── requirements.txt       # Python dependencies
├── test/
│   ├── test_usecase1.py   # Complete test script
│   └── outputs/          # Generated results
└── README.md             # This file
```

## Individual Steps

You can also run steps individually:

```python
from database_setup import setup_db
from load_data import load_master_data, load_raw_data
from validate_data import validate_headers, validate_line_items
from route_data import route_valid_data

# Setup
setup_db('retail_db.sqlite')

# Load data
load_master_data('retail_db.sqlite', '../data')
load_raw_data('retail_db.sqlite', '../data')

# Validate
validate_headers('retail_db.sqlite')
validate_line_items('retail_db.sqlite')

# Route
route_valid_data('retail_db.sqlite')
```

