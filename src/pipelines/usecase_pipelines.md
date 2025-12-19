# Use Case Specific Pipeline Diagrams

## Use Case 1: Data Ingestion and Quality Validation

```
┌─────────────────────────────────────────────────────────────┐
│              USE CASE 1: DATA INGESTION PIPELINE              │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Master Data  │
│ CSV Files    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Load Master Data     │
│ - stores             │
│ - products           │
│ - customers          │
│ - promotions         │
│ - loyalty_rules      │
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│ Sales Data   │
│ CSV Files    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Load Raw Sales Data  │
│ - headers            │
│ - line_items         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Normalize Data       │
│ 1NF: Split multi-    │
│      value cells     │
│ 2NF: Remove partial  │
│      dependencies    │
│ 3NF: Remove trans.   │
│      dependencies    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Validate Headers     │
│ Rule 1: Missing      │
│        customer_id   │
│ Rule 2: Invalid      │
│        store_id      │
│ Rule 3: Invalid      │
│        customer_id   │
│ Rule 4: Invalid date │
│ Rule 5: Invalid      │
│        amount        │
│ Rule 10: Total       │
│         mismatch     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Validate Line Items  │
│ Rule 6: Missing      │
│        product_id    │
│ Rule 7: Invalid      │
│        product_id    │
│ Rule 8: Invalid      │
│        amount        │
│ Rule 9: Invalid      │
│        transaction_id│
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Route Data           │
│                      │
│  Valid Records       │
│  ────────────────►   │
│  staging_* tables    │
│                      │
│  Invalid Records     │
│  ────────────────►   │
│  quarantine_* tables │
└──────────────────────┘
```

## Use Case 2: Promotion Effectiveness Analyzer

```
┌─────────────────────────────────────────────────────────────┐
│         USE CASE 2: PROMOTION EFFECTIVENESS PIPELINE        │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│ Staging Data         │
│ - line_items         │
│ - products           │
│ - promotions         │
└──────┬───────────────┘
       │
       ├──────────────────────────────┐
       │                              │
       ▼                              ▼
┌──────────────────┐        ┌──────────────────┐
│ Calculate        │        │ Calculate        │
│ Baseline Sales   │        │ Promoted Sales   │
│                  │        │                  │
│ Group by:        │        │ Group by:        │
│ - category       │        │ - promotion_id   │
│ - product        │        │ - category       │
│                  │        │                  │
│ WHERE            │        │ WHERE            │
│ promotion_id     │        │ promotion_id     │
│ IS NULL          │        │ IS NOT NULL      │
└──────┬───────────┘        └──────┬───────────┘
       │                          │
       └──────────┬───────────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ Calculate Sales Lift │
       │                      │
       │ Lift % =             │
       │   (Promoted -        │
       │    Baseline) /       │
       │   Baseline * 100      │
       └──────┬───────────────┘
              │
              ▼
       ┌──────────────────────┐
       │ Rank Promotions      │
       │                      │
       │ ORDER BY             │
       │ sales_lift DESC      │
       │                      │
       │ LIMIT 3              │
       └──────┬───────────────┘
              │
              ▼
       ┌──────────────────────┐
       │ Store Results        │
       │ → promotion_         │
       │   effectiveness      │
       └──────────────────────┘
```

## Use Case 3: Loyalty Point Calculation Engine

```
┌─────────────────────────────────────────────────────────────┐
│         USE CASE 3: LOYALTY POINT CALCULATION PIPELINE      │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│ Staging Data         │
│ - sales_header       │
│ - loyalty_rules      │
│ - customers          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Get Unprocessed      │
│ Transactions         │
│                      │
│ WHERE processed = 0  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ For Each Transaction │
│                      │
│ 1. Get amount        │
│ 2. Find applicable   │
│    rule              │
│ 3. Calculate points  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Apply Loyalty Rules  │
│                      │
│ Base Points =        │
│   amount ×           │
│   points_per_unit    │
│                      │
│ Total Points =       │
│   Base + Bonus       │
│   (if threshold met) │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Update Customer      │
│                      │
│ 1. Record in         │
│    loyalty_point_     │
│    transactions      │
│                      │
│ 2. Update customer   │
│    total_loyalty_    │
│    points            │
│                      │
│ 3. Update last_      │
│    purchase_date     │
│                      │
│ 4. Mark transaction  │
│    as processed      │
└──────────────────────┘
```

## Use Case 4: Customer Segmentation

```
┌─────────────────────────────────────────────────────────────┐
│         USE CASE 4: CUSTOMER SEGMENTATION PIPELINE         │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│ Staging Data         │
│ - sales_header       │
│ - customers          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Calculate RFM        │
│ Metrics              │
│                      │
│ R = Recency          │
│   Days since last    │
│   purchase           │
│                      │
│ F = Frequency        │
│   Count of           │
│   transactions      │
│                      │
│ M = Monetary         │
│   Total spend        │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Calculate            │
│ Percentiles          │
│                      │
│ Top 10% threshold    │
│ for monetary value   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Apply Segmentation   │
│ Rules                │
│                      │
│ IF monetary >=       │
│    top_10_threshold  │
│    → High-Spenders   │
│                      │
│ ELSE IF recency >= 60│
│    AND points > 0    │
│    → At-Risk         │
│                      │
│ ELSE                 │
│    → Regular         │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Update Segments      │
│                      │
│ 1. Insert into       │
│    customer_segments │
│                      │
│ 2. Update customer_  │
│    details.segment_id│
└──────────────────────┘
```

## Use Case 5: Loyalty Notification System

```
┌─────────────────────────────────────────────────────────────┐
│         USE CASE 5: NOTIFICATION SYSTEM PIPELINE            │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│ Loyalty Transactions  │
│ (From UC3)           │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Identify Updated     │
│ Customers            │
│                      │
│ JOIN                 │
│ loyalty_point_        │
│ transactions         │
│ WITH                 │
│ customer_details     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ For Each Customer    │
│                      │
│ 1. Get customer info │
│ 2. Get points earned │
│ 3. Get total points  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Generate Email       │
│ Template             │
│                      │
│ Subject:             │
│   "Your Loyalty      │
│    Points Update"    │
│                      │
│ Body:                │
│   Hi {name},         │
│   You earned {new}   │
│   points!             │
│   Total: {total}     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Send Notification    │
│                      │
│ 1. Insert into       │
│    loyalty_          │
│    notifications     │
│                      │
│ 2. Set status =      │
│    'sent'            │
│                      │
│ (Simulated - no      │
│  actual email sent)  │
└──────────────────────┘
```

## Use Case 6: Inventory Analysis

```
┌─────────────────────────────────────────────────────────────┐
│         USE CASE 6: INVENTORY ANALYSIS PIPELINE           │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│ Staging Data         │
│ - line_items         │
│ - products           │
│ - sales_header       │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Identify Top 5       │
│ Products             │
│                      │
│ GROUP BY product_id  │
│ SUM(quantity)        │
│ ORDER BY DESC        │
│ LIMIT 5              │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ For Each Top Product │
│                      │
│ 1. Get product info  │
│ 2. Get sales by store│
│ 3. Calculate metrics │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Analyze by Store     │
│                      │
│ Calculate:           │
│ - Days with sales    │
│ - Total days         │
│ - Out-of-stock days  │
│ - Avg daily sales    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Calculate Metrics    │
│                      │
│ Out-of-Stock % =     │
│   (out_days /        │
│    total_days) × 100 │
│                      │
│ Lost Sales =         │
│   avg_daily ×        │
│   out_days           │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Store Results        │
│                      │
│ → inventory_         │
│   analysis table     │
│                      │
│ Columns:             │
│ - product_id         │
│ - store_id           │
│ - out_of_stock_%     │
│ - estimated_lost_    │
│   sales              │
└──────────────────────┘
```

