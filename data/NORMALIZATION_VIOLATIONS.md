# Normalization Violations in CSV Data

This document explains the denormalization issues intentionally included in the CSV files to demonstrate normalization during data ingestion.

---

## 1NF (First Normal Form) Violations

### Issue: Multiple Values in One Cell

**Location:** `store_sales_line_items.csv`

**Example:**
```
line_item_id,transaction_id,product_id,promotion_id,quantity,line_item_amount
102,TXN067,"P001,P002",PR001,2,200.00
```

**Problem:** The `product_id` column contains multiple values separated by commas ("P001,P002"). This violates 1NF which requires atomic (indivisible) values.

**Normalization:** During ingestion, this will be split into two separate rows:
```
102,TXN067,P001,PR001,1,100.00
103,TXN067,P002,PR001,1,100.00
```

---

## 2NF (Second Normal Form) Violations

### Issue: Partial Dependencies

**Location:** `store_sales_line_items.csv`

**Example:**
```
line_item_id,transaction_id,product_id,promotion_id,quantity,line_item_amount,product_name,product_category
1,TXN001,P001,PR001,2,135.98,Wireless Headphones,Electronics
```

**Problem:** The `product_name` and `product_category` columns depend on `product_id`, not on the primary key `line_item_id`. This is a partial dependency violation of 2NF.

**Normalization:** During ingestion, these columns will be removed from line_items. Product information is already stored in the `products` table and can be joined when needed.

**After Normalization:**
```
line_item_id,transaction_id,product_id,promotion_id,quantity,line_item_amount
1,TXN001,P001,PR001,2,135.98
```

---

## 3NF (Third Normal Form) Violations

### Issue: Transitive Dependencies

**Location:** `store_sales_header.csv`

**Example:**
```
transaction_id,customer_id,store_id,transaction_date,total_amount,store_city,store_region
TXN001,C001,ST001,2024-12-13 10:30:00,159.98,New York,New York
```

**Problem:** The `store_city` and `store_region` columns depend on `store_id`, not on the primary key `transaction_id`. This is a transitive dependency violation of 3NF.

**Normalization:** During ingestion, these columns will be removed from the header table. Store information is already stored in the `stores` table and can be joined when needed.

**After Normalization:**
```
transaction_id,customer_id,store_id,transaction_date,total_amount
TXN001,C001,ST001,2024-12-13 10:30:00,159.98
```

---

## Normalization Process

The normalization happens automatically during data ingestion:

1. **Load Raw Data** → Data is loaded as-is (with violations)
2. **1NF Normalization** → Split multi-value cells into separate rows
3. **2NF Normalization** → Remove partial dependency columns
4. **3NF Normalization** → Remove transitive dependency columns
5. **Validation** → Apply data quality rules
6. **Route to Staging** → Store normalized, validated data

---

## Benefits of Normalization

1. **Eliminates Data Redundancy** → Product/store info stored once
2. **Prevents Update Anomalies** → Update product name in one place
3. **Prevents Insertion Anomalies** → Can't insert inconsistent data
4. **Prevents Deletion Anomalies** → Deleting transaction doesn't delete product info
5. **Improves Data Integrity** → Single source of truth

---

## Summary

| Normal Form | Violation Type | Location | Example |
|-------------|---------------|----------|---------|
| 1NF | Multi-value cells | line_items | `product_id = "P001,P002"` |
| 2NF | Partial dependency | line_items | `product_name`, `product_category` |
| 3NF | Transitive dependency | header | `store_city`, `store_region` |

All violations are automatically corrected during the normalization step before validation.

