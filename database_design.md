# Database Design Documentation
## ER Diagram and Normalization Analysis

This document presents the Entity Relationship (ER) diagram and normalization analysis for the Retail Data Processing System.

---

## Entity Relationship (ER) Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RETAIL DATA PROCESSING SYSTEM                   │
│                              ER DIAGRAM                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   stores     │
├──────────────┤
│ store_id (PK)│
│ store_name   │
│ store_city   │
│ store_region │
│ opening_date │
└──────┬───────┘
       │
       │ 1
       │
       │ M
       │
┌──────▼──────────────────┐
│ store_sales_header       │
├──────────────────────────┤
│ transaction_id (PK)     │
│ customer_id (FK) ────────┼──┐
│ store_id (FK) ───────────┘  │
│ transaction_date         │  │
│ total_amount             │  │
└──────┬───────────────────┘  │
       │                      │
       │ 1                    │
       │                      │
       │ M                    │
       │                      │
┌──────▼──────────────────────┐
│ store_sales_line_items      │
├──────────────────────────────┤
│ line_item_id (PK)          │
│ transaction_id (FK) ────────┘
│ product_id (FK) ────────────┐
│ promotion_id (FK) ───────────┼──┐
│ quantity                    │  │
│ line_item_amount            │  │
└─────────────────────────────┘  │
                                 │
                                 │
┌────────────────────────────────┼──┐
│                                │  │
│  ┌──────────────┐              │  │
│  │  products    │              │  │
│  ├──────────────┤              │  │
│  │ product_id(PK)              │  │
│  │ product_name │              │  │
│  │ product_category            │  │
│  │ unit_price   │              │  │
│  │ current_stock_level         │  │
│  └──────┬───────┘              │  │
│         │                      │  │
│         │ M                    │  │
│         │                      │  │
│  ┌──────▼──────────────────────┼──┘
│  │                              │
│  ┌──────────────┐              │
│  │promotion_    │              │
│  │details       │              │
│  ├──────────────┤              │
│  │ promotion_id(PK)            │
│  │ promotion_name               │
│  │ start_date   │              │
│  │ end_date     │              │
│  │ discount_percentage          │
│  │ applicable_category          │
│  └──────────────────────────────┘
│
│  ┌──────────────────────┐
│  │ customer_details     │
│  ├──────────────────────┤
│  │ customer_id (PK)     │
│  │ first_name           │
│  │ email                │
│  │ loyalty_status       │
│  │ total_loyalty_points │
│  │ last_purchase_date   │
│  │ segment_id           │
│  └──────────────────────┘
│
│  ┌──────────────────────┐
│  │ loyalty_rules        │
│  ├──────────────────────┤
│  │ rule_id (PK)         │
│  │ rule_name            │
│  │ points_per_unit_spend│
│  │ min_spend_threshold  │
│  │ bonus_points         │
│  └──────────────────────┘
│
└─────────────────────────────────┘
```

### Relationship Summary

| Relationship | Type | Description |
|--------------|------|-------------|
| stores → store_sales_header | 1:M | One store can have many transactions |
| store_sales_header → store_sales_line_items | 1:M | One transaction can have many line items |
| products → store_sales_line_items | 1:M | One product can appear in many line items |
| promotion_details → store_sales_line_items | 1:M | One promotion can apply to many line items |
| customer_details → store_sales_header | 1:M | One customer can have many transactions |
| loyalty_rules → customer_details | N:M (via transactions) | Rules applied through transaction processing |

---

## Normalization Analysis

Normalization is the process of organizing data to minimize redundancy and dependency. This database follows **Third Normal Form (3NF)** principles.

---

## 1. First Normal Form (1NF) Analysis

**1NF Requirements:**
- Each column contains atomic (indivisible) values
- Each row is unique
- No repeating groups

### ✅ All Tables Comply with 1NF

| Table | 1NF Compliance | Notes |
|-------|---------------|-------|
| **stores** | ✅ Yes | All attributes are atomic (single values) |
| **products** | ✅ Yes | All attributes are atomic |
| **customer_details** | ✅ Yes | All attributes are atomic |
| **promotion_details** | ✅ Yes | All attributes are atomic |
| **loyalty_rules** | ✅ Yes | All attributes are atomic |
| **store_sales_header** | ✅ Yes | All attributes are atomic |
| **store_sales_line_items** | ✅ Yes | All attributes are atomic |

**Example - Before 1NF (Hypothetical):**
```
❌ BAD: products table with repeating groups
product_id | product_name | categories
P001       | Headphones   | Electronics,Audio,Accessories
```

**Example - After 1NF (Current Design):**
```
✅ GOOD: products table
product_id | product_name | product_category
P001       | Headphones   | Electronics
```
- Each cell contains a single value
- No repeating groups

---

## 2. Second Normal Form (2NF) Analysis

**2NF Requirements:**
- Must be in 1NF
- All non-key attributes must be fully functionally dependent on the primary key
- No partial dependencies

### ✅ All Tables Comply with 2NF

#### Analysis by Table:

#### **stores**
- **Primary Key:** `store_id`
- **Dependencies:**
  - `store_name` → fully dependent on `store_id` ✅
  - `store_city` → fully dependent on `store_id` ✅
  - `store_region` → fully dependent on `store_id` ✅
  - `opening_date` → fully dependent on `store_id` ✅
- **Result:** ✅ **2NF Compliant** - All attributes fully depend on primary key

#### **products**
- **Primary Key:** `product_id`
- **Dependencies:**
  - `product_name` → fully dependent on `product_id` ✅
  - `product_category` → fully dependent on `product_id` ✅
  - `unit_price` → fully dependent on `product_id` ✅
  - `current_stock_level` → fully dependent on `product_id` ✅
- **Result:** ✅ **2NF Compliant**

#### **customer_details**
- **Primary Key:** `customer_id`
- **Dependencies:**
  - `first_name` → fully dependent on `customer_id` ✅
  - `email` → fully dependent on `customer_id` ✅
  - `loyalty_status` → fully dependent on `customer_id` ✅
  - `total_loyalty_points` → fully dependent on `customer_id` ✅
  - `last_purchase_date` → fully dependent on `customer_id` ✅
  - `segment_id` → fully dependent on `customer_id` ✅
- **Result:** ✅ **2NF Compliant**

#### **promotion_details**
- **Primary Key:** `promotion_id`
- **Dependencies:**
  - `promotion_name` → fully dependent on `promotion_id` ✅
  - `start_date` → fully dependent on `promotion_id` ✅
  - `end_date` → fully dependent on `promotion_id` ✅
  - `discount_percentage` → fully dependent on `promotion_id` ✅
  - `applicable_category` → fully dependent on `promotion_id` ✅
- **Result:** ✅ **2NF Compliant**

#### **loyalty_rules**
- **Primary Key:** `rule_id`
- **Dependencies:**
  - `rule_name` → fully dependent on `rule_id` ✅
  - `points_per_unit_spend` → fully dependent on `rule_id` ✅
  - `min_spend_threshold` → fully dependent on `rule_id` ✅
  - `bonus_points` → fully dependent on `rule_id` ✅
- **Result:** ✅ **2NF Compliant**

#### **store_sales_header**
- **Primary Key:** `transaction_id`
- **Foreign Keys:** `customer_id`, `store_id`
- **Dependencies:**
  - `customer_id` → fully dependent on `transaction_id` ✅
  - `store_id` → fully dependent on `transaction_id` ✅
  - `transaction_date` → fully dependent on `transaction_id` ✅
  - `total_amount` → fully dependent on `transaction_id` ✅
- **Result:** ✅ **2NF Compliant**

#### **store_sales_line_items**
- **Primary Key:** `line_item_id`
- **Composite Key Consideration:** `(transaction_id, product_id)` could be composite key
- **Foreign Keys:** `transaction_id`, `product_id`, `promotion_id`
- **Dependencies:**
  - `transaction_id` → fully dependent on `line_item_id` ✅
  - `product_id` → fully dependent on `line_item_id` ✅
  - `promotion_id` → fully dependent on `line_item_id` ✅
  - `quantity` → fully dependent on `line_item_id` ✅
  - `line_item_amount` → fully dependent on `line_item_id` ✅
- **Note:** `line_item_amount` is calculated but stored for performance
- **Result:** ✅ **2NF Compliant**

**Example - Partial Dependency (Avoided):**
```
❌ BAD: If we had combined tables without normalization
transaction_id | product_id | product_name | quantity | line_amount
TXN001         | P001       | Headphones   | 2        | 159.98
```
- `product_name` depends on `product_id`, not `transaction_id` (partial dependency)
- This would violate 2NF

**Current Design (2NF Compliant):**
```
✅ GOOD: Separated tables
store_sales_line_items: transaction_id, product_id, quantity, line_amount
products: product_id, product_name
```
- `product_name` is in `products` table, referenced via foreign key
- No partial dependencies

---

## 3. Third Normal Form (3NF) Analysis

**3NF Requirements:**
- Must be in 2NF
- No transitive dependencies (non-key attributes should not depend on other non-key attributes)
- All non-key attributes must depend only on the primary key

### ✅ All Tables Comply with 3NF

#### Detailed Analysis:

#### **stores**
- **Primary Key:** `store_id`
- **Transitive Dependency Check:**
  - `store_city` → Does it depend on `store_region`? 
    - **No** - A city can exist in multiple regions (e.g., "Springfield" in multiple states)
    - Both are independent attributes of the store
  - **Result:** ✅ **3NF Compliant**

#### **products**
- **Primary Key:** `product_id`
- **Transitive Dependency Check:**
  - `product_category` → Does it determine `unit_price`?
    - **No** - Price is product-specific, not category-specific
  - `unit_price` → Does it determine `current_stock_level`?
    - **No** - Stock level is independent of price
  - **Result:** ✅ **3NF Compliant**

#### **customer_details**
- **Primary Key:** `customer_id`
- **Transitive Dependency Check:**
  - `loyalty_status` → Does it determine `total_loyalty_points`?
    - **No** - Points determine status, not vice versa (status is derived)
    - However, status could be calculated from points, but storing it is acceptable for performance
  - `segment_id` → Does it depend on other attributes?
    - **No** - It's a separate classification attribute
  - **Result:** ✅ **3NF Compliant** (with minor denormalization for performance)

#### **promotion_details**
- **Primary Key:** `promotion_id`
- **Transitive Dependency Check:**
  - `applicable_category` → Does it determine `discount_percentage`?
    - **No** - Discount is promotion-specific, not category-specific
  - **Result:** ✅ **3NF Compliant**

#### **loyalty_rules**
- **Primary Key:** `rule_id`
- **Transitive Dependency Check:**
  - `min_spend_threshold` → Does it determine `bonus_points`?
    - **No** - These are independent rule parameters
  - **Result:** ✅ **3NF Compliant**

#### **store_sales_header**
- **Primary Key:** `transaction_id`
- **Transitive Dependency Check:**
  - `total_amount` → Does it depend on `customer_id` or `store_id`?
    - **No** - It's calculated from line items, specific to transaction
  - **Result:** ✅ **3NF Compliant**

#### **store_sales_line_items**
- **Primary Key:** `line_item_id`
- **Transitive Dependency Check:**
  - `line_item_amount` → Does it depend on `product_id` or `promotion_id`?
    - **No** - It's calculated as: `(unit_price × quantity) - discount`
    - Stored for performance but doesn't create transitive dependency
  - **Result:** ✅ **3NF Compliant**

**Example - Transitive Dependency (Avoided):**
```
❌ BAD: If we had transitive dependency
customer_id | first_name | loyalty_status | status_points_threshold
C001        | John       | Gold           | 1000
```
- If `status_points_threshold` depends on `loyalty_status`, this violates 3NF
- Should be in separate `loyalty_status_rules` table

**Current Design (3NF Compliant):**
```
✅ GOOD: No transitive dependencies
customer_details: customer_id, loyalty_status, total_loyalty_points
loyalty_rules: rule_id, min_spend_threshold, bonus_points
```
- Status and rules are in separate tables
- No transitive dependencies

---

## Normalization Summary Table

| Table Name | 1NF | 2NF | 3NF | Notes |
|------------|-----|-----|-----|-------|
| **stores** | ✅ | ✅ | ✅ | Fully normalized |
| **products** | ✅ | ✅ | ✅ | Fully normalized |
| **customer_details** | ✅ | ✅ | ✅ | Fully normalized (minor denormalization for performance) |
| **promotion_details** | ✅ | ✅ | ✅ | Fully normalized |
| **loyalty_rules** | ✅ | ✅ | ✅ | Fully normalized |
| **store_sales_header** | ✅ | ✅ | ✅ | Fully normalized |
| **store_sales_line_items** | ✅ | ✅ | ✅ | Fully normalized |

**Overall Database Normalization Level: ✅ 3NF (Third Normal Form)**

---

## Key Design Decisions

### 1. **Separate Header and Line Items**
- **Reason:** Follows standard retail data model
- **Benefit:** Allows multiple products per transaction
- **Normalization:** Prevents repeating product groups in header

### 2. **Foreign Key Relationships**
- All foreign keys properly reference primary keys
- Maintains referential integrity
- Enables JOIN operations efficiently

### 3. **Calculated Fields Stored**
- `total_amount` in `store_sales_header` (calculated from line items)
- `line_item_amount` in `store_sales_line_items` (calculated from price × quantity)
- **Reason:** Performance optimization (denormalization for read performance)
- **Trade-off:** Acceptable minor denormalization for query performance

### 4. **No Redundant Data**
- Product details stored once in `products` table
- Store details stored once in `stores` table
- Customer details stored once in `customer_details` table
- **Benefit:** Single source of truth, easy updates

---

## Functional Dependencies

### stores
```
store_id → {store_name, store_city, store_region, opening_date}
```

### products
```
product_id → {product_name, product_category, unit_price, current_stock_level}
```

### customer_details
```
customer_id → {first_name, email, loyalty_status, total_loyalty_points, 
                last_purchase_date, segment_id}
```

### promotion_details
```
promotion_id → {promotion_name, start_date, end_date, discount_percentage, 
                applicable_category}
```

### loyalty_rules
```
rule_id → {rule_name, points_per_unit_spend, min_spend_threshold, bonus_points}
```

### store_sales_header
```
transaction_id → {customer_id, store_id, transaction_date, total_amount}
```

### store_sales_line_items
```
line_item_id → {transaction_id, product_id, promotion_id, quantity, 
                line_item_amount}
```

---

## Database Schema Structure

### Schema Organization
```
Database: retail_processing
├── raw (schema)
│   ├── store_sales_header (raw data)
│   └── store_sales_line_items (raw data)
│
├── staging (schema) - 3NF Normalized
│   ├── stores
│   ├── products
│   ├── customer_details
│   ├── promotion_details
│   ├── loyalty_rules
│   ├── store_sales_header
│   └── store_sales_line_items
│
└── quarantine (schema)
    ├── rejected_sales_header
    └── rejected_sales_line_items
```

---

## Benefits of 3NF Design

1. **Data Integrity**
   - No redundant data storage
   - Single source of truth for each entity
   - Easy to maintain and update

2. **Storage Efficiency**
   - Minimal data duplication
   - Optimal use of database space

3. **Update Efficiency**
   - Update product price in one place (`products` table)
   - All references automatically reflect changes

4. **Query Flexibility**
   - JOIN operations are efficient
   - Supports complex analytical queries

5. **Scalability**
   - Design supports growth
   - Easy to add new attributes or tables

---

## Conclusion

The database design follows **Third Normal Form (3NF)** normalization standards:
- ✅ **1NF:** All tables have atomic values, no repeating groups
- ✅ **2NF:** All non-key attributes fully depend on primary keys
- ✅ **3NF:** No transitive dependencies exist

This design ensures:
- Data consistency and integrity
- Efficient storage and retrieval
- Easy maintenance and updates
- Support for complex analytical queries

The design is suitable for a retail data processing system and can efficiently support all 6 use cases outlined in the requirements.

