# Installation Guide

## Quick Start

### Step 1: Install Python Dependencies

```bash
cd usecase1
pip install -r requirements.txt
```

This installs:
- `pandas` - For CSV reading and data manipulation
- `sqlalchemy` - For database operations

### Step 2: Setup SQLite Database

SQLite is **built-in with Python** - no separate installation needed!

Run the setup script:

```bash
python setup_sqlite.py
```

**Expected Output:**
```
SQLite Setup
==================================================
✓ SQLite 3.x.x is available
✓ Database retail_db.sqlite created

✓ Setup complete! Database: retail_db.sqlite
```

**If you see an error:**
- Make sure you have Python 3.x installed
- SQLite should be included by default
- If not available, reinstall Python or use a different distribution

### Step 3: Run the Test

Execute the complete test script:

```bash
cd test
python test_usecase1.py
```

**What it does:**
1. Creates all database tables
2. Loads master data (stores, products, customers, etc.)
3. Loads raw sales data
4. Applies 10 validation rules
5. Routes valid data to staging
6. Saves all results to `test/outputs/` folder

**Expected Output:**
```
============================================================
USE CASE 1: DATA INGESTION AND VALIDATION
============================================================

[Step 1] Setting up database...
✓ Database tables created

[Step 2] Loading master data...
✓ Loaded stores: 8 records
✓ Loaded products: 15 records
...

[Step 3] Loading raw sales data...
✓ Loaded header: 60 records
✓ Loaded line items: 92 records

[Step 4] Validating header data...
✓ Header validation complete

[Step 5] Validating line items...
✓ Line items validation complete

[Step 6] Routing valid data to staging...
✓ Valid data routed to staging

[Step 7] Saving results...
✓ Results saved to outputs/

============================================================
VALIDATION SUMMARY
============================================================
...
```

## Troubleshooting

### Issue: "Module not found" error

**Solution:** Make sure you're in the correct directory and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "File not found" error for CSV files

**Solution:** Make sure the `data` folder is in the parent directory:
```
hackathon/
├── data/          # CSV files here
└── usecase1/      # Code here
```

### Issue: SQLite not available

**Solution:** This is very rare. SQLite comes with Python. If missing:
- Reinstall Python from python.org
- Or use a different Python distribution (Anaconda, etc.)

## File Structure After Setup

```
usecase1/
├── retail_db.sqlite          # Database file (created by setup)
├── database_setup.py
├── load_data.py
├── validate_data.py
├── route_data.py
├── setup_sqlite.py
├── requirements.txt
├── test/
│   ├── test_usecase1.py
│   └── outputs/              # Results saved here
│       ├── 01_raw_headers.csv
│       ├── 02_raw_line_items.csv
│       ├── 03_rejected_headers.csv
│       ├── 04_rejected_line_items.csv
│       ├── 05_staging_headers.csv
│       ├── 06_staging_line_items.csv
│       ├── 07_validation_summary.csv
│       ├── 08_rejection_reasons_headers.csv
│       └── 09_rejection_reasons_line_items.csv
└── README.md
```

## Verification

After running the test, check the `test/outputs/` folder. You should see 9 CSV files with all intermediate results.

