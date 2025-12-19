# Retail Data Processing System - Complete Implementation

This project implements all 6 use cases for retail data processing as specified in the system requirements.

## Project Structure

```
src/
├── common/              # Shared utilities
│   ├── database.py     # Database setup and connection
│   └── data_loader.py   # Data loading utilities
├── usecase1/           # Data Ingestion and Quality Validation
│   └── data_ingestion.py
├── usecase2/           # Promotion Effectiveness Analyzer
│   └── promotion_analyzer.py
├── usecase3/           # Loyalty Point Calculation Engine
│   └── loyalty_engine.py
├── usecase4/           # Customer Segmentation
│   └── customer_segmentation.py
├── usecase5/           # Loyalty Notification System
│   └── notification_system.py
├── usecase6/           # Inventory Analysis
│   └── inventory_analysis.py
├── tests/              # Test suite
│   └── test_all_usecases.py
├── pipelines/          # Pipeline diagrams
│   ├── global_pipeline.md
│   └── usecase_pipelines.md
├── outputs/            # Generated outputs
├── main.py             # Main pipeline orchestrator
└── README.md           # This file
```

## Installation

1. Install dependencies:
```bash
pip install pandas
```

2. Ensure data files are in the `data/` directory at the project root:
- stores.csv
- products.csv
- customer_details.csv
- promotion_details.csv
- loyalty_rules.csv
- store_sales_header.csv
- store_sales_line_items.csv

## Usage

### Run All Use Cases

```bash
cd src
python main.py
```

### Run Individual Use Case

```python
from common.database import setup_database, get_db_path
from usecase1.data_ingestion import execute as execute_usecase1

db_path = setup_database()
execute_usecase1(db_path)
```

### Run Tests

```bash
cd src
python -m tests.test_all_usecases
```

Or using unittest:

```bash
cd src
python -m unittest tests.test_all_usecases
```

## Use Cases Overview

### Use Case 1: Data Ingestion and Quality Validation
- Loads master and sales data from CSV files
- Normalizes data (1NF, 2NF, 3NF)
- Validates data quality using 10 validation rules
- Routes valid data to staging, invalid to quarantine

### Use Case 2: Promotion Effectiveness Analyzer
- Calculates baseline sales (non-promoted)
- Calculates promoted sales
- Computes sales lift percentage
- Ranks top 3 most effective promotions

### Use Case 3: Loyalty Point Calculation Engine
- Processes transactions and applies loyalty rules
- Calculates points based on transaction amount
- Updates customer loyalty point balances
- Records all point transactions

### Use Case 4: Customer Segmentation
- Calculates RFM (Recency, Frequency, Monetary) metrics
- Segments customers into:
  - High-Spenders (Top 10% by monetary value)
  - At-Risk (60+ days inactive, has points)
  - Regular (others)
- Updates customer segment assignments

### Use Case 5: Loyalty Notification System
- Identifies customers with updated points
- Generates personalized email notifications
- Simulates email sending (logs to database)
- Tracks notification status

### Use Case 6: Inventory Analysis
- Identifies top 5 best-selling products
- Analyzes inventory levels by store
- Calculates out-of-stock percentages
- Estimates lost sales due to stockouts

## Database Schema

The system uses SQLite with the following main tables:

- **Master Data**: `staging_stores`, `staging_products`, `staging_customer_details`, `staging_promotion_details`, `staging_loyalty_rules`
- **Raw Data**: `raw_store_sales_header`, `raw_store_sales_line_items`
- **Quarantine**: `quarantine_rejected_sales_header`, `quarantine_rejected_sales_line_items`
- **Staging**: `staging_store_sales_header`, `staging_store_sales_line_items`
- **Results**: `promotion_effectiveness`, `loyalty_point_transactions`, `customer_segments`, `loyalty_notifications`, `inventory_analysis`

## Pipeline Flow

See `pipelines/global_pipeline.md` for the complete global pipeline diagram and `pipelines/usecase_pipelines.md` for individual use case pipelines.

## Test Coverage

The test suite (`tests/test_all_usecases.py`) includes:
- Unit tests for each use case
- End-to-end pipeline test
- Data validation tests
- Results verification

Run tests to see coverage report.

## Outputs

All outputs are stored in:
- Database tables (see Database Schema above)
- Test reports in `outputs/` directory
- Console logs during execution

## Requirements Coverage

All requirements from `system_requirements.md` are implemented:
- ✅ Use Case 1: Data ingestion with 10 validation rules
- ✅ Use Case 2: Promotion effectiveness analysis with top 3 ranking
- ✅ Use Case 3: Loyalty point calculation with rule-based logic
- ✅ Use Case 4: Customer segmentation with RFM metrics
- ✅ Use Case 5: Automated notification system (simulated)
- ✅ Use Case 6: Inventory analysis with lost sales estimation

## Notes

- SQLite is used for simplicity (no separate database server needed)
- Email notifications are simulated (logged to database)
- All data quality rules are implemented as specified
- Pipeline can be run end-to-end or use cases individually

