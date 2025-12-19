# Global Pipeline - Retail Data Processing System

## Overview
This document describes the complete end-to-end pipeline for processing retail data across all 6 use cases.

## Pipeline Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RETAIL DATA PROCESSING PIPELINE                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: DATA INGESTION & VALIDATION (Use Case 1)                       │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Load Master Data                   │
        │  - stores                           │
        │  - products                         │
        │  - customers                        │
        │  - promotions                       │
        │  - loyalty_rules                    │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Load Raw Sales Data                │
        │  - store_sales_header               │
        │  - store_sales_line_items           │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Normalize Data                     │
        │  - 1NF: Split multi-value cells     │
        │  - 2NF: Remove partial dependencies │
        │  - 3NF: Remove transitive deps      │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Validate Data Quality              │
        │  - Header validation (Rules 1-5,10)  │
        │  - Line items validation (Rules 6-9) │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Route Data                         │
        │  ✓ Valid → staging                  │
        │  ✗ Invalid → quarantine             │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Staging Layer (Clean Data)         │
        └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: PROMOTION ANALYSIS (Use Case 2) - Can run in parallel           │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Calculate Baseline Sales           │
        │  (Non-promoted items by category)   │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Calculate Promoted Sales           │
        │  (Promoted items by promotion)      │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Calculate Sales Lift               │
        │  Lift % = (Promoted - Baseline) /   │
        │            Baseline * 100           │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Rank Top 3 Promotions               │
        │  → promotion_effectiveness table     │
        └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: LOYALTY POINT CALCULATION (Use Case 3)                          │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Get Unprocessed Transactions       │
        │  (processed = 0)                    │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Apply Loyalty Rules                │
        │  - Match transaction amount to rule  │
        │  - Calculate base points            │
        │  - Add bonus points if applicable   │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Update Customer Points             │
        │  - Record in loyalty_point_txns     │
        │  - Update customer_details          │
        │  - Mark transaction as processed    │
        └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: CUSTOMER SEGMENTATION (Use Case 4)                               │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Calculate RFM Metrics              │
        │  - Recency: Days since last purchase│
        │  - Frequency: # of transactions     │
        │  - Monetary: Total spend            │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Apply Segmentation Rules            │
        │  - High-Spenders: Top 10% by $      │
        │  - At-Risk: 60+ days, has points    │
        │  - Regular: Others                 │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Update Customer Segments           │
        │  → customer_segments table          │
        │  → customer_details.segment_id      │
        └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 5: LOYALTY NOTIFICATIONS (Use Case 5) - Depends on Use Case 3     │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Identify Updated Customers          │
        │  (From loyalty_point_transactions)   │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Generate Email Templates            │
        │  - Personalize with customer name    │
        │  - Include points earned             │
        │  - Show total balance                │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Send Notifications                 │
        │  → loyalty_notifications table       │
        │  (Simulated - status = 'sent')      │
        └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 6: INVENTORY ANALYSIS (Use Case 6) - Can run independently          │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Identify Top 5 Products            │
        │  (By total quantity sold)           │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Analyze Inventory by Store         │
        │  - Calculate out-of-stock days      │
        │  - Calculate out-of-stock %         │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Estimate Lost Sales                │
        │  = Avg daily sales × Out-of-stock   │
        │    days                             │
        └──────────────┬──────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────┐
        │  Store Results                      │
        │  → inventory_analysis table         │
        └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          OUTPUT & REPORTS                                │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  Generate Reports                    │
        │  - Validation summary                │
        │  - Promotion effectiveness           │
        │  - Customer segments                 │
        │  - Inventory analysis                │
        │  - Test coverage                     │
        └─────────────────────────────────────┘
```

## Execution Order

1. **Use Case 1** (Required first): Data Ingestion and Validation
2. **Use Case 2** (Can run after UC1): Promotion Analysis
3. **Use Case 3** (Requires UC1): Loyalty Point Calculation
4. **Use Case 4** (Requires UC1): Customer Segmentation
5. **Use Case 5** (Requires UC3): Loyalty Notifications
6. **Use Case 6** (Requires UC1): Inventory Analysis

## Dependencies

```
UC1 → UC2 (optional)
UC1 → UC3 → UC5
UC1 → UC4
UC1 → UC6
```

## Data Flow

```
CSV Files → Raw Layer → Validation → Staging Layer → Use Cases → Results Tables
```

