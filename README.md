# 💳 Payment Transaction Monitoring

A data analytics and monitoring project built with **Python, PostgreSQL, SQL, and Streamlit**.

---

## 📌 Project Overview

This project monitors payment transactions and identifies **failed, pending, cancelled, and delayed transactions**.

The system generates payment transaction data, stores it in PostgreSQL, analyzes the data using SQL, and presents the results through an interactive Streamlit dashboard.

The project simulates a real-world payment monitoring system where analysts can monitor transaction activity, identify operational issues, and analyze customer, merchant, and payment-method performance.

---

## 🎯 Project Objectives

- Monitor payment transaction activity
- Identify delayed transactions
- Analyze transaction success and failure rates
- Monitor payment method performance
- Analyze merchant performance
- Analyze customer transaction behavior
- Track daily transaction volume and value
- Build an interactive monitoring dashboard

---

## 🏗️ Project Architecture


Python
   ↓
Transaction Data Generation
   ↓
PostgreSQL Database
   ↓
SQL Analysis
   ↓
Pandas
   ↓
Streamlit Dashboard


## 🛠️ Technologies Used

Python – Transaction data generation
PostgreSQL – Database storage
SQL – Data analysis and monitoring
Pandas – Data processing
Streamlit – Interactive dashboard
psycopg2 – PostgreSQL connection
Git & GitHub – Version control

## 🗄️ Database
The project uses PostgreSQL to store payment transaction data.

## Main Tables

## Customers
Stores customer information.
customer_id
name
country
created_at

## Merchants
Stores merchant information.
merchant_id
name
country
created_at

## Payment Methods
Stores available payment methods.
payment_method_id
method_name

## Transactions
Stores payment transaction information.
transaction_id
customer_id
merchant_id
payment_method_id
amount
status
created_at
completed_at

## 📊 Transaction Status

The system supports four transaction statuses:

Status	Description
SUCCESS	Transaction completed successfully
FAILED	Transaction failed
PENDING	Transaction is still being processed
CANCELLED	Transaction was cancelled

## 🚨 Delayed Transaction Rule

A transaction is considered delayed when:

Status is PENDING
Pending duration is greater than or equal to 10 seconds
``
NOW() - created_at >= INTERVAL '10 seconds'

The dashboard identifies these transactions and displays them in the Delayed Transactions section.

## 📈 Dashboard Features
### 🔴 Live Payment Monitoring

The dashboard provides real-time transaction monitoring including:

Total transactions
Successful transactions
Failed transactions
Pending transactions
Delayed transactions
Success rate
Total transaction value
Delayed transaction alerts

### 📊 Transaction Analytics

The dashboard provides historical transaction analysis including:

Daily transaction volume
Daily transaction value
Payment method failure rate
Merchant performance
Customer transaction analysis
Date-range filtering


## 💳 Payment Method Analysis

The project calculates the failure rate for each payment method.

Example metrics:

Payment Method
      ↓
Total Transactions
      ↓
Failed Transactions
      ↓
Failure Rate

Failure rate is calculated as:

Failed Transactions / Total Transactions × 100

## 🏪 Merchant Performance

Merchant-level analysis includes:

Total transactions
Failed transactions
Failure rate
Total transaction value

This helps identify merchants with higher transaction failure rates.

## 👤 Customer Analysis

Customer-level analysis includes:

Total transactions
Total transaction value
Failed transactions

This helps identify high-value and high-activity customers.

## 📅 Daily Transaction Analysis

The dashboard tracks transaction activity by date.

Metrics include:

Daily transaction count
Daily transaction value

This helps identify changes and unusual spikes in transaction activity

## 📸 Dashboard Screenshots

## 🔴 Live Payment Monitoring
![Dashboard Overview](screenshots/dashboard_overview.png)

## 📊 Payment & Transaction Analysis
![Payment Analysis](screenshots/payment_analysis.png)

## 👤 Customer & Merchant Analysis
![Customer Merchant Analysis](screenshots/customer_merchant_analysis.png)

