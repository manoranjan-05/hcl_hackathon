# Use Case 1: Data Ingestion and Validation Pipeline

## Pipeline Overview

This document shows the step-by-step data flow with block diagrams for the Data Ingestion and Quality Validation pipeline.

---

## High-Level Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘

    CSV Files (data/)
           │
           ▼
    ┌──────────────┐
    │  Step 1:     │  Create Database Schemas & Tables
    │  Setup DB    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Step 2:     │  Load Master Data (stores, products, etc.)
    │  Load Master │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Step 3:     │  Load Raw Sales Data (header + line items)
    │  Load Raw    │  (May contain denormalized data)
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Step 3.5:   │  Normalize Data (1NF, 2NF, 3NF)
    │  Normalize   │  Remove denormalization issues
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Step 4:     │  Apply 10 Validation Rules
    │  Validate    │
    └──────┬───────┘
           │
           ├──────────────┐
           │              │
           ▼              ▼
    ┌──────────┐    ┌──────────────┐
    │  Valid   │    │  Rejected    │
    │  Data    │    │  Data        │
    └────┬─────┘    └──────┬───────┘
         │                 │
         ▼                 ▼
    ┌──────────┐    ┌──────────────┐
    │ Staging  │    │ Quarantine   │
    │ Schema   │    │ Schema       │
    └──────────┘    └──────────────┘
```

---

## Step 1: Database Setup

```
┌─────────────────────────────────────────┐
│         STEP 1: DATABASE SETUP          │
└─────────────────────────────────────────┘

    ┌──────────────┐
    │  Create DB   │
    │  File        │
    └──────┬───────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  Create Tables in SQLite            │
    │                                     │
    │  raw_store_sales_header             │
    │  raw_store_sales_line_items         │
    │                                     │
    │  quarantine_rejected_sales_header   │
    │  quarantine_rejected_sales_line_... │
    │                                     │
    │  staging_store_sales_header         │
    │  staging_store_sales_line_items     │
    └─────────────────────────────────────┘
```

**Code:** `database_setup.py`

---

## Step 2: Load Master Data

```
┌─────────────────────────────────────────┐
│      STEP 2: LOAD MASTER DATA          │
└─────────────────────────────────────────┘

    ┌──────────────┐
    │  CSV Files   │
    └──────┬───────┘
           │
           ├─── stores.csv ───────────┐
           ├─── products.csv ─────────┤
           ├─── customer_details.csv ─┤
           ├─── promotion_details.csv─┤
           └─── loyalty_rules.csv ────┤
                                      │
                                      ▼
    ┌─────────────────────────────────────┐
    │  Load to staging_* tables             │
    │                                       │
    │  staging_stores                      │
    │  staging_products                    │
    │  staging_customer_details            │
    │  staging_promotion_details           │
    │  staging_loyalty_rules               │
    └─────────────────────────────────────┘
```

**Code:** `load_data.py` → `load_master_data()`

---

## Step 3: Load Raw Sales Data

```
┌─────────────────────────────────────────┐
│     STEP 3: LOAD RAW SALES DATA         │
└─────────────────────────────────────────┘

    ┌──────────────────────┐
    │  store_sales_header   │
    │  .csv                 │
    │  (May contain:        │
    │   store_city,         │
    │   store_region)       │
    └──────┬────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  raw_store_sales_header              │
    │  (Denormalized - contains transitive │
    │   dependencies - 3NF violation)      │
    └─────────────────────────────────────┘

    ┌──────────────────────┐
    │  store_sales_line_   │
    │  items.csv           │
    │  (May contain:       │
    │   product_name,      │
    │   product_category,  │
    │   multiple product_ids)│
    └──────┬───────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  raw_store_sales_line_items          │
    │  (Denormalized - contains:          │
    │   - Multi-value cells - 1NF violation│
    │   - Partial dependencies - 2NF violation)│
    └─────────────────────────────────────┘
```

**Code:** `load_data.py` → `load_raw_data()`

---

## Step 3.5: Normalize Data

```
┌─────────────────────────────────────────┐
│      STEP 3.5: NORMALIZE DATA            │
└─────────────────────────────────────────┘

    ┌──────────────────────┐
    │  Denormalized Data   │
    └──────┬───────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  1NF NORMALIZATION                   │
    │  - Split multi-value cells           │
    │  - Remove repeating groups           │
    │  Example: "P001,P002" → 2 rows       │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  2NF NORMALIZATION                   │
    │  - Remove partial dependencies       │
    │  - Remove product_name,             │
    │    product_category from line_items  │
    │  (These depend on product_id,        │
    │   not line_item_id)                  │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  3NF NORMALIZATION                   │
    │  - Remove transitive dependencies    │
    │  - Remove store_city, store_region   │
    │    from header                       │
    │  (These depend on store_id,          │
    │   not transaction_id)                │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  Normalized Data (1NF, 2NF, 3NF)    │
    │  Ready for validation                │
    └─────────────────────────────────────┘
```

**Code:** `normalize_data.py` → `normalize_all()`

**Normalization Examples:**

**1NF Violation (Before):**
```
line_item_id | product_id | quantity
102          | P001,P002  | 2
```

**1NF Normalized (After):**
```
line_item_id | product_id | quantity
102          | P001       | 1
103          | P002       | 1
```

**2NF Violation (Before):**
```
line_item_id | product_id | product_name        | quantity
1            | P001       | Wireless Headphones | 2
```

**2NF Normalized (After):**
```
line_item_id | product_id | quantity
1            | P001       | 2
```
*(product_name removed - stored in products table)*

**3NF Violation (Before):**
```
transaction_id | store_id | store_city  | store_region
TXN001         | ST001    | New York    | New York
```

**3NF Normalized (After):**
```
transaction_id | store_id
TXN001         | ST001
```
*(store_city, store_region removed - stored in stores table)*

---

## Step 4: Data Validation

```
┌─────────────────────────────────────────┐
│      STEP 4: DATA VALIDATION            │
└─────────────────────────────────────────┘

    ┌──────────────────────┐
    │  Raw Header Data     │
    └──────┬───────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  HEADER VALIDATION RULES            │
    │                                     │
    │  Rule 1: Missing customer_id      │
    │  Rule 2: Invalid store_id         │
    │  Rule 3: Invalid customer_id       │
    │  Rule 4: Invalid transaction_date  │
    │  Rule 5: total_amount ≤ 0          │
    │  Rule 10: Total ≠ Sum of items     │
    └──────┬──────────────────────────────┘
           │
           ├──────────────┐
           │              │
           ▼              ▼
    ┌──────────┐    ┌──────────────┐
    │  Valid   │    │  Rejected    │
    │          │    │  → Quarantine│
    └──────────┘    └──────────────┘

    ┌──────────────────────┐
    │  Raw Line Items Data  │
    └──────┬───────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  LINE ITEMS VALIDATION RULES         │
    │                                     │
    │  Rule 6: Missing product_id        │
    │  Rule 7: Invalid product_id        │
    │  Rule 8: line_item_amount ≤ 0      │
    │  Rule 9: Invalid transaction_id    │
    └──────┬──────────────────────────────┘
           │
           ├──────────────┐
           │              │
           ▼              ▼
    ┌──────────┐    ┌──────────────┐
    │  Valid   │    │  Rejected    │
    │          │    │  → Quarantine│
    └──────────┘    └──────────────┘
```

**Code:** `validate_data.py` → `validate_headers()`, `validate_line_items()`

---

## Step 5: Route Valid Data

```
┌─────────────────────────────────────────┐
│      STEP 5: ROUTE VALID DATA           │
└─────────────────────────────────────────┘

    ┌──────────────────────┐
    │  Valid Headers        │
    │  (Not in quarantine)  │
    └──────┬───────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  staging_store_sales_header          │
    │  (Clean, validated data)             │
    └─────────────────────────────────────┘

    ┌──────────────────────┐
    │  Valid Line Items     │
    │  (Not in quarantine)  │
    │  AND                  │
    │  transaction_id in    │
    │  valid headers        │
    └──────┬───────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │  staging_store_sales_line_items      │
    │  (Clean, validated data)             │
    └─────────────────────────────────────┘
```

**Code:** `route_data.py` → `route_valid_data()`

---

## Complete Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                             │
└──────────────────────────────────────────────────────────────────┘

CSV Files
    │
    ├─── Master Data ───────────────────────────────────┐
    │    (stores, products, customers, etc.)             │
    │                                                    │
    │                                                    ▼
    │                                            ┌──────────────┐
    │                                            │  Staging     │
    │                                            │  Master      │
    │                                            │  Tables      │
    │                                            └──────┬───────┘
    │                                                   │
    └─── Sales Data ────────────────────────────────────┤
         (header, line_items)                           │
              │                                         │
              ▼                                         │
    ┌─────────────────┐                                │
    │  Raw Schema     │                                │
    │  (Unvalidated)  │                                │
    └────────┬────────┘                                │
             │                                         │
             ▼                                         │
    ┌─────────────────────────────────────────┐       │
    │  VALIDATION ENGINE                      │       │
    │                                         │       │
    │  ┌─────────────────────────────────┐   │       │
    │  │  Check against Master Data      │   │       │
    │  │  Apply 10 Validation Rules      │   │       │
    │  └─────────────────────────────────┘   │       │
    └────────┬────────────────┬───────────────┘       │
             │                │                       │
             │                │                       │
    ┌────────▼────────┐ ┌─────▼──────────┐           │
    │  Valid Data     │ │  Rejected Data │           │
    │                 │ │                │           │
    └────────┬────────┘ └─────┬──────────┘           │
             │                │                       │
             │                ▼                       │
             │         ┌──────────────┐               │
             │         │  Quarantine │               │
             │         │  Schema     │               │
             │         └──────────────┘               │
             │                                         │
             ▼                                         │
    ┌─────────────────┐                               │
    │  Staging Schema │                               │
    │  (Validated)    │◄──────────────────────────────┘
    └─────────────────┘
             │
             ▼
    ┌─────────────────┐
    │  Output Files   │
    │  (CSV Reports)  │
    └─────────────────┘
```

---

## Validation Rules Flow

```
┌─────────────────────────────────────────────────────────────┐
│              VALIDATION RULES EXECUTION                     │
└─────────────────────────────────────────────────────────────┘

Header Records
    │
    ├─→ Rule 1: customer_id NULL/empty? ──┐
    ├─→ Rule 2: store_id exists? ──────────┤
    ├─→ Rule 3: customer_id exists? ───────┤
    ├─→ Rule 4: transaction_date valid? ───┤
    ├─→ Rule 5: total_amount > 0? ────────┤
    └─→ Rule 10: total = sum(items)? ───────┤
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │  Reject?     │
                                    └──┬───────┬───┘
                                       │       │
                                    Yes│       │No
                                       │       │
                                       ▼       ▼
                              ┌──────────┐ ┌──────────┐
                              │Quarantine│ │  Valid   │
                              └──────────┘ └──────────┘

Line Item Records
    │
    ├─→ Rule 6: product_id NULL/empty? ────┐
    ├─→ Rule 7: product_id exists? ─────────┤
    ├─→ Rule 8: line_item_amount > 0? ─────┤
    └─→ Rule 9: transaction_id exists? ─────┤
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │  Reject?     │
                                    └──┬───────┬───┘
                                       │       │
                                    Yes│       │No
                                       │       │
                                       ▼       ▼
                              ┌──────────┐ ┌──────────┐
                              │Quarantine│ │  Valid   │
                              └──────────┘ └──────────┘
```

---

## Output Generation

```
┌─────────────────────────────────────────┐
│      OUTPUT FILES GENERATION            │
└─────────────────────────────────────────┘

    ┌──────────────────────┐
    │  Database Tables     │
    └──────┬───────────────┘
           │
           ├─── Raw Data ────────────────┐
           ├─── Rejected Data ───────────┤
           ├─── Staging Data ────────────┤
           └─── Summary Stats ───────────┤
                                        │
                                        ▼
    ┌─────────────────────────────────────┐
    │  Export to CSV Files                │
    │                                     │
    │  01_raw_headers.csv                 │
    │  02_raw_line_items.csv              │
    │  03_rejected_headers.csv            │
    │  04_rejected_line_items.csv         │
    │  05_staging_headers.csv             │
    │  06_staging_line_items.csv          │
    │  07_validation_summary.csv          │
    │  08_rejection_reasons_headers.csv    │
    │  09_rejection_reasons_line_items.csv│
    └─────────────────────────────────────┘
```

**Code:** `test/test_usecase1.py` → `save_results()`

---

## Execution Sequence

```
┌─────────────────────────────────────────────────────────────┐
│              EXECUTION SEQUENCE                            │
└─────────────────────────────────────────────────────────────┘

    START
      │
      ▼
    [Setup Database]
      │
      ▼
    [Load Master Data]
      │
      ▼
    [Load Raw Sales Data]
      │  (May contain denormalized data)
      ▼
    [Normalize Data]
      │  (1NF: Split multi-values)
      │  (2NF: Remove partial deps)
      │  (3NF: Remove transitive deps)
      ▼
    [Validate Headers]
      │
      ├───→ [Reject Invalid] ──→ [Quarantine]
      │
      └───→ [Keep Valid]
             │
             ▼
    [Validate Line Items]
      │
      ├───→ [Reject Invalid] ──→ [Quarantine]
      │
      └───→ [Keep Valid]
             │
             ▼
    [Route Valid Data to Staging]
      │
      ▼
    [Generate Output Files]
      │
      ▼
    [Print Summary]
      │
      ▼
    END
```

---

## Key Components

| Component | File | Function |
|-----------|------|----------|
| Database Setup | `database_setup.py` | Creates all tables |
| Data Loading | `load_data.py` | Loads CSV to database |
| Normalization | `normalize_data.py` | Normalizes to 1NF, 2NF, 3NF |
| Validation | `validate_data.py` | Applies 10 validation rules |
| Data Routing | `route_data.py` | Routes valid data to staging |
| Test Runner | `test/test_usecase1.py` | Executes complete pipeline |

---

## Data Quality Metrics

```
┌─────────────────────────────────────────┐
│      VALIDATION METRICS                 │
└─────────────────────────────────────────┘

    Total Records
         │
         ├─── Header Records
         │    ├─── Valid: X records
         │    └─── Rejected: Y records
         │         └─── Validation Rate: Z%
         │
         └─── Line Item Records
              ├─── Valid: X records
              └─── Rejected: Y records
                   └─── Validation Rate: Z%
```

---

This pipeline ensures data quality by:
1. ✅ Accepting all raw data without filtering
2. ✅ Applying comprehensive validation rules
3. ✅ Preserving rejected data for analysis
4. ✅ Routing only clean data to staging
5. ✅ Generating detailed reports

