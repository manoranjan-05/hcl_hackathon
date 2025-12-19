# Database Design - ER Diagram & Normalization

## Entity Relationship (ER) Diagram

```
┌──────────────┐
│   stores     │◄────┐
│ store_id (PK)│     │
└──────┬───────┘     │
       │ 1:M         │
       │             │
┌──────▼─────────────┼──┐
│ store_sales_header │  │
│ transaction_id(PK)│  │
│ customer_id (FK)──┼──┼──┐
│ store_id (FK)──────┘  │  │
│ transaction_date      │  │
│ total_amount          │  │
└──────┬───────────────┘  │  │
       │ 1:M              │  │
       │                  │  │
┌──────▼──────────────────┼──┼──┐
│ store_sales_line_items  │  │  │
│ line_item_id (PK)      │  │  │
│ transaction_id (FK)─────┘  │  │
│ product_id (FK)────────────┼──┼──┐
│ promotion_id (FK)─────────┼──┼──┼──┐
│ quantity                  │  │  │  │
│ line_item_amount          │  │  │  │
└───────────────────────────┘  │  │  │
                                │  │  │
┌───────────────────────────────┼──┘  │
│ products                      │     │
│ product_id (PK)               │     │
│ product_name                  │     │
│ product_category              │     │
│ unit_price                    │     │
│ current_stock_level           │     │
└───────────────────────────────┘     │
                                       │
┌──────────────────────────────────────┼──┐
│ promotion_details                    │  │
│ promotion_id (PK)                    │  │
│ promotion_name                       │  │
│ start_date, end_date                 │  │
│ discount_percentage                  │  │
│ applicable_category                  │  │
└──────────────────────────────────────┘  │
                                          │
┌─────────────────────────────────────────┼──┐
│ customer_details                        │  │
│ customer_id (PK)                        │  │
│ first_name, email                       │  │
│ loyalty_status                          │  │
│ total_loyalty_points                    │  │
│ last_purchase_date                     │  │
│ segment_id                             │  │
└─────────────────────────────────────────┘  │
                                             │
┌────────────────────────────────────────────┘
│ loyalty_rules
│ rule_id (PK)
│ rule_name
│ points_per_unit_spend
│ min_spend_threshold
│ bonus_points
└────────────────────────────────────────────
```

### Relationships

| From | To | Type | Description |
|------|-----|------|-------------|
| stores | store_sales_header | 1:M | One store → Many transactions |
| customer_details | store_sales_header | 1:M | One customer → Many transactions |
| store_sales_header | store_sales_line_items | 1:M | One transaction → Many line items |
| products | store_sales_line_items | 1:M | One product → Many line items |
| promotion_details | store_sales_line_items | 1:M | One promotion → Many line items |

---

## Normalization Analysis

### Summary: All tables are in **3NF (Third Normal Form)**

| Table | 1NF | 2NF | 3NF |
|-------|-----|-----|-----|
| stores | ✅ | ✅ | ✅ |
| products | ✅ | ✅ | ✅ |
| customer_details | ✅ | ✅ | ✅ |
| promotion_details | ✅ | ✅ | ✅ |
| loyalty_rules | ✅ | ✅ | ✅ |
| store_sales_header | ✅ | ✅ | ✅ |
| store_sales_line_items | ✅ | ✅ | ✅ |

---

## Normalization Details

### 1NF (First Normal Form) ✅
**Requirement:** Atomic values, no repeating groups

**Compliance:** All tables have single atomic values in each cell.

**Example:**
- ✅ `product_category` = "Electronics" (single value)
- ❌ Would violate: `product_category` = "Electronics,Audio,Accessories" (multiple values)

---

### 2NF (Second Normal Form) ✅
**Requirement:** Must be 1NF + All non-key attributes fully depend on primary key

**Compliance:** All attributes depend entirely on their primary keys.

**Key Design:**
- Product details (name, price) are in `products` table, not duplicated in `store_sales_line_items`
- Store details are in `stores` table, referenced via foreign key
- No partial dependencies exist

---

### 3NF (Third Normal Form) ✅
**Requirement:** Must be 2NF + No transitive dependencies

**Compliance:** No non-key attribute depends on another non-key attribute.

**Key Design:**
- `loyalty_status` and `total_loyalty_points` are independent (status could be derived but stored for performance)
- `store_city` and `store_region` are independent attributes
- All attributes depend only on primary key

---

## Functional Dependencies

```
stores:           store_id → {store_name, store_city, store_region, opening_date}
products:         product_id → {product_name, product_category, unit_price, current_stock_level}
customer_details: customer_id → {first_name, email, loyalty_status, total_loyalty_points, last_purchase_date, segment_id}
promotion_details: promotion_id → {promotion_name, start_date, end_date, discount_percentage, applicable_category}
loyalty_rules:    rule_id → {rule_name, points_per_unit_spend, min_spend_threshold, bonus_points}
store_sales_header: transaction_id → {customer_id, store_id, transaction_date, total_amount}
store_sales_line_items: line_item_id → {transaction_id, product_id, promotion_id, quantity, line_item_amount}
```

---

## Design Benefits

✅ **Data Integrity** - Single source of truth for each entity  
✅ **Storage Efficiency** - Minimal data duplication  
✅ **Update Efficiency** - Update once, reflects everywhere  
✅ **Query Performance** - Efficient JOINs and aggregations  
✅ **Scalability** - Easy to extend with new attributes

---

## Schema Structure

```
Database: retail_processing
├── raw (raw data ingestion)
├── staging (3NF normalized tables)
└── quarantine (rejected records)
```
