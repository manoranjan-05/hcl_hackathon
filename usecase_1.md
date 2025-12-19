# Use Case 1: Data Ingestion and Quality Validation

## Overview

Step-by-step SQL queries to ingest sales data from CSV files, validate quality, and route clean data to staging while quarantining bad data.

**Prerequisites:** Database created, CSV files available, master data loaded in `staging` schema.

---

## Step 1: Create Schemas

```sql
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS quarantine;
```

---

## Step 2: Create Tables

### Raw Tables (Unvalidated Data)

```sql
-- Raw Header Table
CREATE TABLE IF NOT EXISTS raw.store_sales_header (
    transaction_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20),
    store_id VARCHAR(10),
    transaction_date TIMESTAMP,
    total_amount DECIMAL(10,2),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw Line Items Table
CREATE TABLE IF NOT EXISTS raw.store_sales_line_items (
    line_item_id INT PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(20),
    promotion_id VARCHAR(10),
    quantity INT,
    line_item_amount DECIMAL(10,2),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Quarantine Tables (Rejected Data)

```sql
-- Quarantine Header Table
CREATE TABLE IF NOT EXISTS quarantine.rejected_sales_header (
    transaction_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20),
    store_id VARCHAR(10),
    transaction_date TIMESTAMP,
    total_amount DECIMAL(10,2),
    rejection_reason VARCHAR(500),
    rejection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quarantine Line Items Table
CREATE TABLE IF NOT EXISTS quarantine.rejected_sales_line_items (
    line_item_id INT PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(20),
    promotion_id VARCHAR(10),
    quantity INT,
    line_item_amount DECIMAL(10,2),
    rejection_reason VARCHAR(500),
    rejection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Staging Tables (Validated Data)

```sql
-- Staging Header Table
CREATE TABLE IF NOT EXISTS staging.store_sales_header (
    transaction_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    store_id VARCHAR(10) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES staging.customer_details(customer_id),
    FOREIGN KEY (store_id) REFERENCES staging.stores(store_id)
);

-- Staging Line Items Table
CREATE TABLE IF NOT EXISTS staging.store_sales_line_items (
    line_item_id INT PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    promotion_id VARCHAR(10),
    quantity INT NOT NULL,
    line_item_amount DECIMAL(10,2) NOT NULL,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES staging.store_sales_header(transaction_id),
    FOREIGN KEY (product_id) REFERENCES staging.products(product_id),
    FOREIGN KEY (promotion_id) REFERENCES staging.promotion_details(promotion_id)
);
```

---

## Step 3: Load CSV Data into Raw Tables

```sql
-- PostgreSQL: Load Header Data
COPY raw.store_sales_header (transaction_id, customer_id, store_id, transaction_date, total_amount)
FROM 'data/store_sales_header.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- PostgreSQL: Load Line Items Data
COPY raw.store_sales_line_items (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount)
FROM 'data/store_sales_line_items.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- MySQL Alternative:
-- LOAD DATA LOCAL INFILE 'data/store_sales_header.csv' INTO TABLE raw.store_sales_header
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
```

---

## Step 4: Apply Data Quality Validation Rules

### Header Validation Rules

```sql
-- Rule 1: Missing/NULL customer_id
INSERT INTO quarantine.rejected_sales_header 
SELECT *, 'REJECTED: Missing or NULL customer_id' AS rejection_reason
FROM raw.store_sales_header
WHERE customer_id IS NULL OR customer_id = '' OR customer_id = 'INVALID';

-- Rule 2: Invalid store_id
INSERT INTO quarantine.rejected_sales_header 
SELECT r.*, 'REJECTED: Invalid store_id' AS rejection_reason
FROM raw.store_sales_header r
LEFT JOIN staging.stores s ON r.store_id = s.store_id
WHERE s.store_id IS NULL
  AND r.transaction_id NOT IN (SELECT transaction_id FROM quarantine.rejected_sales_header);

-- Rule 3: Invalid customer_id
INSERT INTO quarantine.rejected_sales_header 
SELECT r.*, 'REJECTED: Invalid customer_id' AS rejection_reason
FROM raw.store_sales_header r
LEFT JOIN staging.customer_details c ON r.customer_id = c.customer_id
WHERE c.customer_id IS NULL
  AND r.transaction_id NOT IN (SELECT transaction_id FROM quarantine.rejected_sales_header);

-- Rule 4: Invalid transaction_date
INSERT INTO quarantine.rejected_sales_header 
SELECT *, 'REJECTED: Invalid transaction_date' AS rejection_reason
FROM raw.store_sales_header
WHERE transaction_date IS NULL
  AND transaction_id NOT IN (SELECT transaction_id FROM quarantine.rejected_sales_header);

-- Rule 5: Invalid total_amount (<= 0)
INSERT INTO quarantine.rejected_sales_header 
SELECT *, 'REJECTED: Invalid total_amount' AS rejection_reason
FROM raw.store_sales_header
WHERE total_amount <= 0
  AND transaction_id NOT IN (SELECT transaction_id FROM quarantine.rejected_sales_header);

-- Rule 10: Header total ≠ Sum of line items
INSERT INTO quarantine.rejected_sales_header 
SELECT h.*, CONCAT('REJECTED: Total mismatch (', h.total_amount, ' vs ', COALESCE(SUM(l.line_item_amount), 0), ')') AS rejection_reason
FROM raw.store_sales_header h
LEFT JOIN raw.store_sales_line_items l ON h.transaction_id = l.transaction_id
WHERE h.transaction_id NOT IN (SELECT transaction_id FROM quarantine.rejected_sales_header)
GROUP BY h.transaction_id, h.customer_id, h.store_id, h.transaction_date, h.total_amount
HAVING ABS(h.total_amount - COALESCE(SUM(l.line_item_amount), 0)) > 0.01;
```

### Line Items Validation Rules

```sql
-- Rule 6: Missing/NULL product_id
INSERT INTO quarantine.rejected_sales_line_items 
SELECT *, 'REJECTED: Missing product_id' AS rejection_reason
FROM raw.store_sales_line_items
WHERE product_id IS NULL OR product_id = '';

-- Rule 7: Invalid product_id
INSERT INTO quarantine.rejected_sales_line_items 
SELECT r.*, 'REJECTED: Invalid product_id' AS rejection_reason
FROM raw.store_sales_line_items r
LEFT JOIN staging.products p ON r.product_id = p.product_id
WHERE p.product_id IS NULL
  AND r.line_item_id NOT IN (SELECT line_item_id FROM quarantine.rejected_sales_line_items);

-- Rule 8: Invalid line_item_amount (<= 0)
INSERT INTO quarantine.rejected_sales_line_items 
SELECT *, 'REJECTED: Invalid line_item_amount' AS rejection_reason
FROM raw.store_sales_line_items
WHERE line_item_amount <= 0
  AND line_item_id NOT IN (SELECT line_item_id FROM quarantine.rejected_sales_line_items);

-- Rule 9: Invalid transaction_id
INSERT INTO quarantine.rejected_sales_line_items 
SELECT r.*, 'REJECTED: Invalid transaction_id' AS rejection_reason
FROM raw.store_sales_line_items r
LEFT JOIN raw.store_sales_header h ON r.transaction_id = h.transaction_id
WHERE h.transaction_id IS NULL
  AND r.line_item_id NOT IN (SELECT line_item_id FROM quarantine.rejected_sales_line_items);
```

---

## Step 5: Route Valid Data to Staging

```sql
-- Insert valid headers
INSERT INTO staging.store_sales_header 
    (transaction_id, customer_id, store_id, transaction_date, total_amount)
SELECT transaction_id, customer_id, store_id, transaction_date, total_amount
FROM raw.store_sales_header
WHERE transaction_id NOT IN (SELECT transaction_id FROM quarantine.rejected_sales_header);

-- Insert valid line items
INSERT INTO staging.store_sales_line_items 
    (line_item_id, transaction_id, product_id, promotion_id, quantity, line_item_amount)
SELECT r.line_item_id, r.transaction_id, r.product_id, r.promotion_id, r.quantity, r.line_item_amount
FROM raw.store_sales_line_items r
WHERE r.line_item_id NOT IN (SELECT line_item_id FROM quarantine.rejected_sales_line_items)
  AND r.transaction_id IN (SELECT transaction_id FROM staging.store_sales_header);
```

---

## Step 6: Verify Results

```sql
-- Validation Summary
SELECT 
    'Header Records' AS record_type,
    COUNT(*) AS total,
    (SELECT COUNT(*) FROM staging.store_sales_header) AS valid,
    (SELECT COUNT(*) FROM quarantine.rejected_sales_header) AS rejected,
    ROUND((SELECT COUNT(*) FROM staging.store_sales_header) * 100.0 / COUNT(*), 2) AS validation_rate
FROM raw.store_sales_header
UNION ALL
SELECT 
    'Line Item Records',
    COUNT(*),
    (SELECT COUNT(*) FROM staging.store_sales_line_items),
    (SELECT COUNT(*) FROM quarantine.rejected_sales_line_items),
    ROUND((SELECT COUNT(*) FROM staging.store_sales_line_items) * 100.0 / COUNT(*), 2)
FROM raw.store_sales_line_items;

-- Rejection Reasons Analysis
SELECT rejection_reason, COUNT(*) AS count
FROM quarantine.rejected_sales_header
GROUP BY rejection_reason
ORDER BY count DESC;
```

---

## Data Quality Rules Summary

| Rule | Validation | Applies To |
|------|------------|------------|
| 1 | Missing/NULL customer_id | Header |
| 2 | Invalid store_id | Header |
| 3 | Invalid customer_id | Header |
| 4 | Invalid transaction_date | Header |
| 5 | total_amount ≤ 0 | Header |
| 6 | Missing/NULL product_id | Line Items |
| 7 | Invalid product_id | Line Items |
| 8 | line_item_amount ≤ 0 | Line Items |
| 9 | Invalid transaction_id | Line Items |
| 10 | Header total ≠ Sum of line items | Header + Line Items |

---

## Execution Order

1. Create schemas (Step 1)
2. Create all tables (Step 2)
3. Load CSV data to raw (Step 3)
4. Apply validation rules (Step 4)
5. Route valid data to staging (Step 5)
6. Verify results (Step 6)
