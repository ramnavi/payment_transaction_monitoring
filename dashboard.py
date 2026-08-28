import streamlit as st
import psycopg2
import pandas as pd
from datetime import date, timedelta
from python.config import DB_CONFIG


# --------------------------------
# Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Payment Transaction Monitoring",
    page_icon="💳",
    layout="wide"
)


# --------------------------------
# Title
# --------------------------------

st.title("💳 Payment Transaction Monitoring")
st.caption("Payment transaction monitoring and analytics")


# --------------------------------
# Manual Refresh
# --------------------------------

if st.button("🔄 Refresh Monitoring"):
    st.rerun()


# ================================================
# 🔴 LIVE MONITORING
# ================================================

st.header("🔴 Live Monitoring")


# --------------------------------
# Connect to PostgreSQL
# --------------------------------

connection = psycopg2.connect(**DB_CONFIG)


# --------------------------------
# Live KPI Query
# --------------------------------

kpi_query = """
SELECT
    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE status = 'SUCCESS'
    ) AS successful_transactions,

    COUNT(*) FILTER (
        WHERE status = 'FAILED'
    ) AS failed_transactions,

    COUNT(*) FILTER (
        WHERE status = 'PENDING'
    ) AS pending_transactions,

    COUNT(*) FILTER (
        WHERE status = 'CANCELLED'
    ) AS cancelled_transactions,

    COUNT(*) FILTER (
        WHERE status = 'PENDING'
        AND NOW() - created_at >= INTERVAL '10 seconds'
    ) AS delayed_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE status = 'SUCCESS'
        )::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS success_rate,

    ROUND(SUM(amount), 2) AS total_transaction_value

FROM transactions;
"""


df = pd.read_sql(kpi_query, connection)

connection.close()


# --------------------------------
# Live KPI Cards
# --------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Transactions",
    df.loc[0, "total_transactions"]
)

col2.metric(
    "Successful",
    df.loc[0, "successful_transactions"]
)

col3.metric(
    "Failed",
    df.loc[0, "failed_transactions"]
)

col4.metric(
    "Pending",
    df.loc[0, "pending_transactions"]
)

col5.metric(
    "Delayed 🚨",
    df.loc[0, "delayed_transactions"]
)


# --------------------------------
# Additional Live KPIs
# --------------------------------

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Success Rate",
        f"{df.loc[0, 'success_rate']}%"
    )

with col2:
    st.metric(
        "Transaction Value",
        f"₹{df.loc[0, 'total_transaction_value']:,.2f}"
    )


# ================================================
# 🚨 LIVE DELAYED TRANSACTIONS
# ================================================

st.subheader("🚨 Delayed Transactions")


connection = psycopg2.connect(**DB_CONFIG)


delayed_query = """
SELECT
    t.transaction_id,
    c.name AS customer,
    m.name AS merchant,
    pm.method_name AS payment_method,
    t.amount,
    t.created_at,
    NOW() - t.created_at AS pending_duration

FROM transactions t

LEFT JOIN customers c
    ON t.customer_id = c.customer_id

LEFT JOIN merchants m
    ON t.merchant_id = m.merchant_id

LEFT JOIN payment_methods pm
    ON t.payment_method_id = pm.payment_method_id

WHERE t.status = 'PENDING'
AND NOW() - t.created_at >= INTERVAL '10 seconds'

ORDER BY pending_duration DESC;
"""


delayed_df = pd.read_sql(delayed_query, connection)

connection.close()


if len(delayed_df) > 0:

    st.warning(
        f"⚠️ {len(delayed_df)} delayed transactions detected!"
    )

    st.dataframe(
        delayed_df,
        use_container_width=True
    )

else:

    st.success(
        "✅ No delayed transactions detected."
    )


# ================================================
# 📊 ANALYTICS
# ================================================

st.divider()

st.header("📊 Analytics")


st.write("Select a date range to analyze historical transactions.")


# --------------------------------
# Date Filters
# --------------------------------

col1, col2 = st.columns(2)


with col1:

    start_date = st.date_input(
        "From",
        value=date.today() - timedelta(days=7)
    )


with col2:

    end_date = st.date_input(
        "To",
        value=date.today()
    )


# Check date range

if start_date > end_date:

    st.error("❌ 'From' date cannot be after 'To' date.")

    st.stop()


# ================================================
# 📈 DAILY TRANSACTION TREND
# ================================================

st.subheader("📈 Daily Transaction Trend")


connection = psycopg2.connect(**DB_CONFIG)


daily_query = """
SELECT
    DATE(created_at) AS transaction_date,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS transaction_value

FROM transactions

WHERE created_at >= %s
AND created_at < %s + INTERVAL '1 day'

GROUP BY DATE(created_at)

ORDER BY transaction_date;
"""


daily_df = pd.read_sql(
    daily_query,
    connection,
    params=(start_date, end_date)
)


connection.close()


if not daily_df.empty:

    st.line_chart(
        daily_df.set_index("transaction_date")[
            ["transaction_count"]
        ]
    )

else:

    st.info("No transactions found for the selected dates.")


# ================================================
# 💰 DAILY TRANSACTION VALUE
# ================================================

st.subheader("💰 Daily Transaction Value")


if not daily_df.empty:

    st.line_chart(
        daily_df.set_index("transaction_date")[
            ["transaction_value"]
        ]
    )


# ================================================
# 🚨 PAYMENT METHOD FAILURE RATE
# ================================================

st.subheader("🚨 Failure Rate by Payment Method")


connection = psycopg2.connect(**DB_CONFIG)


payment_query = """
SELECT
    pm.method_name,

    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE t.status = 'FAILED'
    ) AS failed_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE t.status = 'FAILED'
        )::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS failure_rate

FROM transactions t

LEFT JOIN payment_methods pm
    ON pm.payment_method_id = t.payment_method_id

WHERE t.created_at >= %s
AND t.created_at < %s + INTERVAL '1 day'

GROUP BY
    pm.payment_method_id,
    pm.method_name

ORDER BY failure_rate DESC;
"""


payment_df = pd.read_sql(
    payment_query,
    connection,
    params=(start_date, end_date)
)


connection.close()


st.dataframe(
    payment_df,
    use_container_width=True
)


# ================================================
# 🏪 MERCHANT PERFORMANCE
# ================================================

st.subheader("🏪 Merchant Performance")


connection = psycopg2.connect(**DB_CONFIG)


merchant_query = """
SELECT
    m.name AS merchant,

    COUNT(t.transaction_id) AS total_transactions,

    COUNT(*) FILTER (
        WHERE t.status = 'FAILED'
    ) AS failed_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE t.status = 'FAILED'
        )::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS failure_rate,

    ROUND(
        COALESCE(SUM(t.amount), 0),
        2
    ) AS total_transaction_value

FROM merchants m

LEFT JOIN transactions t
    ON m.merchant_id = t.merchant_id
    AND t.created_at >= %s
    AND t.created_at < %s + INTERVAL '1 day'

GROUP BY
    m.merchant_id,
    m.name

ORDER BY failure_rate DESC;
"""


merchant_df = pd.read_sql(
    merchant_query,
    connection,
    params=(start_date, end_date)
)


connection.close()


st.dataframe(
    merchant_df,
    use_container_width=True
)


# ================================================
# 👤 CUSTOMER ANALYSIS
# ================================================

st.subheader("👤 Customer Transaction Analysis")


connection = psycopg2.connect(**DB_CONFIG)


customer_query = """
SELECT
    c.name AS customer,

    COUNT(t.transaction_id) AS total_transactions,

    ROUND(
        COALESCE(SUM(t.amount), 0),
        2
    ) AS total_transaction_value,

    COUNT(*) FILTER (
        WHERE t.status = 'FAILED'
    ) AS failed_transactions

FROM customers c

LEFT JOIN transactions t
    ON c.customer_id = t.customer_id
    AND t.created_at >= %s
    AND t.created_at < %s + INTERVAL '1 day'

GROUP BY
    c.customer_id,
    c.name

ORDER BY total_transaction_value DESC;
"""


customer_df = pd.read_sql(
    customer_query,
    connection,
    params=(start_date, end_date)
)


connection.close()


st.dataframe(
    customer_df,
    use_container_width=True
)


# ================================================
# 📋 DAILY SUMMARY TABLE
# ================================================

st.subheader("📋 Daily Transaction Summary")


if not daily_df.empty:

    st.dataframe(
        daily_df,
        use_container_width=True
    )