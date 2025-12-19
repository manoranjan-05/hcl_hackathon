# Retail Data Processing Hackathon – Use Cases & Requirements

These use cases cover the **full lifecycle from data ingestion to customer engagement**.

---

## 1. Automated Data Ingestion and Quality Validation Pipeline

### Goal
Establish a robust system for ingesting **high-volume sales data** and ensuring its **quality before processing**.

### Key Steps / Focus
1. Develop a component to ingest `store_sales_header` and `store_sales_line_items` from CSV files.
2. Load them into a raw schema/layer in Database.
3. Define and apply data quality rules (e.g., check for missing `product_id`, negative `sales_amount`, invalid `store_id`, invalid `sales_date` and header total amount not matching line item total).
4. Load clean data into tables in the staging schema.
5. Segregate bad data (reject records) into a dedicated “quarantine” table for later analysis and reporting.

### Entities Involved
- stores
- products
- store_sales_header
- store_sales_line_items

---

## 2. Real-Time Promotion Effectiveness Analyzer

### Goal
Determine which promotions are genuinely driving sales lift per product category shortly after data ingestion.

### Key Steps / Focus
1. Join the clean sales data (`store_sales_line_items`) with the `promotion_details` table using the appropriate promotion key.
2. Calculate the total sales volume and revenue for items purchased under a specific promotion versus the baseline (non-promoted items).
3. Generate a simple dashboard or report ranking the top 3 most effective promotions by sales percentage increase.

### Entities Involved
- store_sales_line_items
- promotion_details
- products

---

## 3. Loyalty Point Calculation Engine

### Goal
Accurately calculate and accrue loyalty points for every eligible customer transaction.

### Key Steps / Focus
1. Join `store_sales_header` (to get the transaction total/date) with `customer_details` (to identify the customer) and `loyalty_rules`.
2. Implement the loyalty calculation logic defined in `loyalty_rules` (e.g., $1 = 1 point, bonus 50 points for purchases over $100).
3. Calculate the accrued points for the current transaction.
4. Update the customer’s total point balance in the `customer_details` table.

### Entities Involved
- store_sales_header
- customer_details
- loyalty_rules

---

## 4. Customer Segmentation for Targeted Offers

### Goal
Use sales history and loyalty data to identify and segment high-value customers for personalized promotions.

### Key Steps / Focus
1. Calculate key RFM (Recency, Frequency, Monetary) metrics for each customer using aggregated sales data.
2. Use the current loyalty point balance as an additional segmentation factor.
3. Create two distinct customer segments:
   - “High-Spenders” (Top 10% by total monetary value)
   - “At-Risk” (Customers who haven’t shopped in 60+ days but have a point balance)

### Entities Involved
- customer_details
- store_sales_header

---

## 5. Automated Loyalty Notification System

### Goal
Complete the loyalty loop by communicating the value earned to the customer via email.

### Key Steps / Focus
1. After the Loyalty Point Calculation Engine runs (Use Case 3), identify customers whose point balance has just been updated.
2. Join the updated balance with the customer’s email address from `customer_details`.
3. Generate a dynamic, personalized email template confirming the newly earned points and the customer’s total accrued points.
4. (Simulate) the process of sending the email notification to the customer.

### Entities Involved
- customer_details

---

## 6. Inventory and Store Performance Correlation

### Goal
Analyze how local store inventory levels correlate with customer purchasing behavior and sales success.

### Key Steps / Focus
1. Integrate (or assume a join with) a table containing daily store inventory levels by product.
2. Join sales data (`store_sales_line_items`) with the store and product information.
3. Identify the Top 5 best-selling products overall.
4. For these top products:
   - Calculate the percentage of days they were out-of-stock at various stores
   - Estimate the potential lost sales if out-of-stock items were purchased

### Entities Involved
- stores
- products
- store_sales_line_items

---

## Notes
1. Create these datasets with any popular Gen AI LLM capabilities. Use right prompt so that datasets are not disjoint.
2. Simulate data quality issues by injecting anomalies.
3. Create multiple datasets for sales data, simulating 7 days of data for multiple stores.
4. Promotion data should have multiple promotions for different products.
5. Use Python/Java or any other cloud-based ETL tool and capabilities of your choice.
6. For database you may use postgres or mysql or any other databases or cloud data lake/data lake of your choice.
7. For dashboard, use open source/python capabilities or any other tool of your choice.

---

## Attribute Sets for Each Data Entity

### 1. stores (Store Information)
- store_id: INT / VARCHAR(10) — Primary Key, Unique identifier for the store.
- store_name: VARCHAR(100) — Name of the store location.
- store_city: VARCHAR(50) — City where the store is located.
- store_region: VARCHAR(50) — Geographical region/state of the store.
- opening_date: DATE — The date the store opened.

### 2. products (Product Catalog)
- product_id: INT / VARCHAR(20) — Primary Key, Unique identifier for the product.
- product_name: VARCHAR(100) — Full name of the product.
- product_category: VARCHAR(50) — Category (e.g., “Electronics”, “Apparel”).
- unit_price: DECIMAL(10,2) — Standard selling price per unit.
- current_stock_level: INT — Current inventory count (useful for Use Case 6).

### 3. customer_details (Customer and Loyalty Data)
- customer_id: INT / VARCHAR(20) — Primary Key, Unique identifier for the customer.
- first_name: VARCHAR(50) — Customer’s first name.
- email: VARCHAR(100) — Customer’s primary email address (Used for Use Case 5).
- loyalty_status: VARCHAR(20) — (e.g., “Bronze”, “Gold”).
- total_loyalty_points: INT — Accumulated loyalty points (Used for Use Case 3 & 5).
- last_purchase_date: DATE — Date of the most recent transaction (Used for Use Case 4/RFM).
- segment_id: VARCHAR(10) — Current segment (“HS”, “AR”, etc.) (Used for Use Case 4).

### 4. promotion_details (Promotion Rules)
- promotion_id: INT / VARCHAR(10) — Primary Key, Unique ID for the promotion.
- promotion_name: VARCHAR(100) — Descriptive name of the promotion.
- start_date: DATE — Date promotion starts.
- end_date: DATE — Date promotion ends.
- discount_percentage: DECIMAL(5,2) — Percentage discount (e.g., 0.10 for 10%).
- applicable_category: VARCHAR(50) — Product category the promotion applies to (or “ALL”).

### 5. loyalty_rules (Point Earning Logic)
- rule_id: INT — Primary Key, Unique ID for the rule.
- rule_name: VARCHAR(100) — (e.g., “Standard Earning”, “Weekend Bonus”).
- points_per_unit_spend: DECIMAL(5,2) — Points earned per monetary unit (e.g., 1.0 for 1 point per $1).
- min_spend_threshold: DECIMAL(10,2) — Minimum required purchase amount to trigger the rule.
- bonus_points: INT — Fixed bonus points awarded if condition is met.

### 6. store_sales_header (Transaction Header)
- transaction_id: INT / VARCHAR(30) — Primary Key, Unique ID for the entire transaction.
- customer_id: INT / VARCHAR(20) — Foreign Key to customer_details.
- store_id: INT / VARCHAR(10) — Foreign Key to stores.
- transaction_date: DATETIME — Date and time of the transaction.
- total_amount: DECIMAL(10,2) — Sum of all line items (Used for Loyalty Calc).

### 7. store_sales_line_items (Transaction Details)
- line_item_id: INT — Primary Key, Unique ID for the line item (can be composite with transaction_id).
- transaction_id: INT / VARCHAR(30) — Foreign Key to store_sales_header.
- product_id: INT / VARCHAR(20) — Foreign Key to products.
- promotion_id: INT / VARCHAR(10) — Foreign Key to promotion_details (Can be NULL if no promo).
- quantity: INT — Number of units purchased.
- line_item_amount: DECIMAL(10,2) — Line total amount.
