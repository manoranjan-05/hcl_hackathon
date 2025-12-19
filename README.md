# Retail Data Processing & Analytics Pipeline

A scalable, end-to-end retail data processing and analytics system built for the **HCLTech Hackathon**.  
This project demonstrates the complete lifecycle of retail data — from ingestion and quality validation to analytics, customer segmentation, and automated notifications — using clean data engineering and analytics best practices.

---

## 📌 Problem Statement Summary

The hackathon problem focuses on designing a **robust retail data platform** that can:

1. Ingest high-volume transactional data
2. Enforce strong data quality rules
3. Generate actionable business insights
4. Enable customer-centric analytics and engagement

The solution is structured around **6 real-world retail use cases**, each mapped to a clean, modular pipeline.

---

## 🎯 Objectives

- Build a **reliable data ingestion and validation pipeline**
- Generate **meaningful, high-quality synthetic datasets** suitable for ML training
- Enable **promotion effectiveness analysis**
- Implement **loyalty point calculation and notifications**
- Perform **customer segmentation using RFM analysis**
- Analyze **inventory impact on sales performance**
- Maintain **data quality, traceability, and scalability**

---

## 🧠 Use Case Overview (Problem Statement Sections)

### 1. Automated Data Ingestion & Quality Validation
- Ingest sales header and line item data from CSV
- Load raw data without validation
- Apply business data quality rules
- Route clean data to staging and bad data to quarantine

### 2. Real-Time Promotion Effectiveness Analyzer
- Compare promoted vs non-promoted sales
- Measure sales lift by promotion and category
- Rank top-performing promotions

### 3. Loyalty Point Calculation Engine
- Apply rule-based loyalty logic per transaction
- Accrue and update customer loyalty points
- Maintain transaction-level traceability

### 4. Customer Segmentation for Targeted Offers
- Compute RFM (Recency, Frequency, Monetary) metrics
- Segment customers into:
  - **High-Spenders**
  - **At-Risk Customers**

### 5. Automated Loyalty Notification System
- Generate personalized loyalty emails
- Simulate email delivery via logs or tables
- Close the customer engagement loop

### 6. Inventory & Store Performance Correlation
- Identify top-selling products
- Analyze stock-out impact
- Estimate potential lost sales

---

## 🏗️ High-Level Architecture
```````````````````

CSV Files
↓
Raw Schema (No Validation)
↓
Data Quality Rules Engine
├── Clean Data → Staging Schema
└── Bad Data → Quarantine Schema
↓
Analytics & Business Logic Layer
├── Promotion Analysis
├── Loyalty Engine
├── Customer Segmentation
└── Inventory Correlation
↓
Reporting / Dashboards / Notifications
```````````````````
--------
<img width="5228" height="2250" alt="image" src="https://github.com/user-attachments/assets/9e178007-afeb-4ceb-93ba-6431095575a2" />

---

## 🗄️ Database Design

- Fully normalized **3NF relational schema**
- Clear separation of concerns:
  - **Raw schema** – raw ingested data
  - **Staging schema** – clean, validated data
  - **Quarantine schema** – rejected records with error reasons
- Standard retail entities:
  - Stores, Products, Customers
  - Sales Header & Line Items
  - Promotions & Loyalty Rules

> Design follows industry-standard retail transaction modeling.

---

## 🔄 Data Generation Strategy

- Synthetic data generated using **LLM-assisted pipelines**
- Ensures:
  - Referential integrity across entities
  - Realistic sales, promotion, and customer behavior
  - Controlled injection of data quality issues
- Simulates:
  - Multiple stores
  - Multiple promotions
  - 7+ days of transactional data

📄 Detailed planning is documented separately in `dataset_generation.md`.

---

## 🧪 Data Quality Rules (Examples)

- `product_id` must not be NULL
- `line_item_amount` must be positive
- `store_id` and `customer_id` must exist
- `transaction_date` must be valid
- Header `total_amount` must match sum of line items

Rejected records are preserved for auditing and analysis.

---

## ⚙️ Technology Stack

| Layer | Tools |
|-----|------|
| Language | Python 3 |
| Data Processing | pandas, SQL |
| Database | PostgreSQL / MySQL |
| Visualization | matplotlib / plotly |
| Orchestration | Python scripts |
| Data Format | CSV → Database |
| ML Readiness | Clean, labeled datasets |

---

## 📁 Repository Structure
````````````

├── data/
│ ├── raw/
│ ├── generated/
│ └── reference/
├── ingestion/
├── data_quality/
├── analytics/
│ ├── promotion_analysis/
│ ├── loyalty_engine/
│ ├── segmentation/
│ └── inventory_analysis/
├── notifications/
├── dataset_generation.md
├── README.md
└── requirements.txt
```````````


---

## 👥 Team Responsibilities
``````````
| Team Member | Responsibility |
|-----------|---------------|
| **Prateek** | Usecase 1 |
| **Surabhi** | Usecase 4 |
| **Ravindar** | Usecase 5 and 6 |
| **Manoranjan** | Usecase 2 and 3 |

---

## 🧩 Design Principles

- **Simplicity first** – clear, readable pipelines
- **Modularity** – each use case independently runnable
- **Traceability** – no silent data loss
- **Scalability** – easy to extend for ML & real-time use
- **Industry-aligned modeling** – real retail data patterns

---

## 🚀 Future Enhancements

- Real-time streaming ingestion (Kafka)
- ML-based customer churn prediction
- Promotion recommendation engine
- Cloud-native orchestration (Airflow)
- Real email/SMS notification integration

---

## 📜 License

This project is developed as part of the **HCLTech Hackathon** and is intended for educational and demonstration purposes.

---

## 🙌 Acknowledgements

- HCLTech Hackathon Team
- Open-source Python ecosystem
- Retail data modeling best practices
