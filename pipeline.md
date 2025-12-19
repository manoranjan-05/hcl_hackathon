# Retail Data Processing Pipeline - Solution Approach

This document outlines a **simple, minimalist approach** to solve each requirement. The approach is designed to be easy to understand and implement by college students.

---

## Overview

The pipeline processes retail sales data through 6 main use cases:
1. Data Ingestion & Quality Validation
2. Promotion Effectiveness Analysis
3. Loyalty Point Calculation
4. Customer Segmentation
5. Loyalty Notification System
6. Inventory & Store Performance Analysis

---

## Use Case 1: Automated Data Ingestion and Quality Validation Pipeline

### Goal
Ingest sales data from CSV files, validate quality, and separate good data from bad data.

### Approach
**Simple 3-Step Process:**

1. **Load Raw Data**
   - Read `store_sales_header.csv` and `store_sales_line_items.csv`
   - Insert all records into `raw_schema.store_sales_header` and `raw_schema.store_sales_line_items` tables
   - No validation at this stage - accept everything as-is

2. **Apply Data Quality Rules**
   - Check each record against these rules:
     - ✅ `product_id` must not be NULL or empty
     - ✅ `sales_amount` (line_item_amount) must be positive (> 0)
     - ✅ `store_id` must exist in `stores` table
     - ✅ `customer_id` must exist in `customer_details` table (or be NULL if allowed)
     - ✅ `sales_date` (transaction_date) must be valid date format
     - ✅ Header `total_amount` must equal sum of related line items
   
3. **Route Data**
   - **Good Data** → Insert into `staging_schema.store_sales_header` and `staging_schema.store_sales_line_items`
   - **Bad Data** → Insert into `quarantine_schema.rejected_sales_header` and `quarantine_schema.rejected_sales_line_items` with reason codes

### Why This Approach?
- **Separation of concerns**: Raw → Staging → Quarantine keeps data organized
- **Simple validation**: One pass through data with clear rules
- **Easy debugging**: Bad data is preserved with reasons for later analysis

### Implementation Tools
- **Python**: Use `pandas` to read CSV and `sqlalchemy` to write to database
- **Database**: PostgreSQL or MySQL with 3 schemas (raw, staging, quarantine)

---

## Use Case 2: Real-Time Promotion Effectiveness Analyzer

### Goal
Find which promotions drive the most sales lift.

### Approach
**Simple 3-Step Calculation:**

1. **Calculate Baseline Sales**
   - Sum sales for products **without** promotion (promotion_id IS NULL)
   - Group by product category
   - Calculate average sales per product

2. **Calculate Promoted Sales**
   - Join `store_sales_line_items` with `promotion_details`
   - Sum sales for products **with** promotion
   - Group by promotion_id and product category

3. **Calculate Lift & Rank**
   - For each promotion: `Sales Lift % = ((Promoted Sales - Baseline Sales) / Baseline Sales) * 100`
   - Rank promotions by sales lift percentage
   - Return top 3 promotions

### Why This Approach?
- **Simple math**: Compare promoted vs non-promoted sales
- **Clear metric**: Percentage increase is easy to understand
- **Actionable**: Top 3 promotions can be easily identified

### Implementation Tools
- **SQL**: Use JOIN and GROUP BY for aggregation
- **Python**: Use `pandas` for calculations or pure SQL queries
- **Dashboard**: Use `matplotlib` or `plotly` for simple bar chart

---

## Use Case 3: Loyalty Point Calculation Engine

### Goal
Calculate and update loyalty points for each transaction.

### Approach
**Simple Rule-Based Calculation:**

1. **Get Transaction Details**
   - Join `store_sales_header` with `customer_details` to get customer info
   - Get `total_amount` from transaction

2. **Apply Loyalty Rules**
   - Read `loyalty_rules` table
   - Find matching rule based on `min_spend_threshold`:
     - If `total_amount >= min_spend_threshold`, apply that rule
     - Use highest threshold that applies
   - Calculate points: `(total_amount * points_per_unit_spend) + bonus_points`

3. **Update Customer Balance**
   - Add calculated points to `customer_details.total_loyalty_points`
   - Update `last_purchase_date` to current transaction date

### Why This Approach?
- **Rule-based**: Simple if-else logic matching transaction amount to rules
- **Incremental**: Add points to existing balance
- **Traceable**: Each transaction's points can be logged

### Implementation Tools
- **SQL**: Use CASE statements or JOIN with loyalty_rules
- **Python**: Use simple if-else logic or pandas apply function

---

## Use Case 4: Customer Segmentation for Targeted Offers

### Goal
Identify high-value customers and at-risk customers.

### Approach
**Simple RFM + Loyalty Analysis:**

1. **Calculate RFM Metrics**
   - **Recency**: Days since `last_purchase_date` (from `customer_details`)
   - **Frequency**: Count of transactions per customer (from `store_sales_header`)
   - **Monetary**: Sum of `total_amount` per customer (from `store_sales_header`)

2. **Create Segments**
   - **High-Spenders (HS)**:
     - Calculate 90th percentile of total monetary value
     - Customers above this threshold → assign `segment_id = 'HS'`
   
   - **At-Risk (AR)**:
     - Customers where `last_purchase_date < (today - 60 days)` AND `total_loyalty_points > 0`
     - Assign `segment_id = 'AR'`

3. **Update Customer Details**
   - Update `customer_details.segment_id` with calculated segment

### Why This Approach?
- **Simple thresholds**: Use percentile and date comparison
- **Clear segments**: Two distinct groups for targeted marketing
- **Easy to understand**: RFM is a standard retail concept

### Implementation Tools
- **SQL**: Use window functions (PERCENTILE_CONT) and date functions
- **Python**: Use `pandas` quantile() and date arithmetic

---

## Use Case 5: Automated Loyalty Notification System

### Goal
Send email notifications to customers after points are updated.

### Approach
**Simple Email Template Generation:**

1. **Identify Updated Customers**
   - After Use Case 3 runs, identify customers with updated `total_loyalty_points`
   - Join with `customer_details` to get email addresses

2. **Generate Email Content**
   - Create simple email template:
     ```
     Subject: Your Loyalty Points Update
     Body: Hi {first_name}, you earned {new_points} points! 
           Your total balance is now {total_loyalty_points} points.
     ```

3. **Simulate Email Sending**
   - Instead of actually sending emails, write to a log file or `notifications` table
   - Format: `customer_id, email, subject, body, status='sent'`

### Why This Approach?
- **No external dependencies**: Simulate instead of real email service
- **Simple template**: String formatting is easy to understand
- **Traceable**: All notifications are logged

### Implementation Tools
- **Python**: Use string formatting or `jinja2` for templates
- **Logging**: Write to CSV or database table

---

## Use Case 6: Inventory and Store Performance Correlation

### Goal
Analyze how inventory levels affect sales.

### Approach
**Simple Stock-Out Analysis:**

1. **Identify Top 5 Products**
   - Sum `quantity` sold from `store_sales_line_items`
   - Group by `product_id`
   - Rank and select top 5

2. **Calculate Stock-Out Days**
   - For each top product and store:
     - Check `products.current_stock_level` (assume daily snapshot)
     - Count days where `current_stock_level = 0`
     - Calculate: `Stock-Out % = (Days Out of Stock / Total Days) * 100`

3. **Estimate Lost Sales**
   - For each stock-out day:
     - Use average daily sales for that product as baseline
     - Lost Sales = Average Daily Sales × Stock-Out Days

### Why This Approach?
- **Simple calculation**: Count zero-stock days
- **Clear metric**: Percentage of time out of stock
- **Actionable**: Identifies products needing better inventory management

### Implementation Tools
- **SQL**: Use window functions for ranking and aggregation
- **Python**: Use `pandas` for grouping and calculations

---

## Overall Pipeline Flow

```
1. Data Ingestion (Use Case 1)
   ↓
2. Promotion Analysis (Use Case 2) - Can run in parallel
   ↓
3. Loyalty Calculation (Use Case 3)
   ↓
4. Customer Segmentation (Use Case 4)
   ↓
5. Notification System (Use Case 5) - Depends on Use Case 3
   ↓
6. Inventory Analysis (Use Case 6) - Can run independently
```

---

## Key Design Principles

1. **Simplicity First**: Use basic SQL and Python, avoid complex frameworks
2. **Clear Separation**: Each use case is independent and can be run separately
3. **Data Preservation**: Bad data is quarantined, not deleted
4. **Incremental Processing**: Process new transactions as they arrive
5. **Easy Testing**: Each step produces clear output that can be verified

---

## Technology Stack Recommendation

- **Language**: Python 3.x
- **Data Processing**: pandas, sqlalchemy
- **Database**: PostgreSQL (or MySQL)
- **Visualization**: matplotlib or plotly (for dashboards)
- **File Format**: CSV (input) → Database (processing) → CSV/JSON (output)

---

## Next Steps

1. Set up database schemas (raw, staging, quarantine)
2. Implement Use Case 1 (Data Ingestion)
3. Test with dummy dataset
4. Implement remaining use cases one by one
5. Create simple dashboard for Use Case 2 results

