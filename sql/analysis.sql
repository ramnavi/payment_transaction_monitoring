-- Overall transaction health
SELECT
    status,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY status
ORDER BY transaction_count DESC;

--Delayed transactions 🚨
SELECT
    transaction_id,
    customer_id,
    merchant_id,
    amount,
    status,
    created_at,
    NOW() - created_at AS pending_duration
FROM transactions
WHERE status = 'PENDING'
AND NOW() - created_at >= INTERVAL '10 seconds';

--Number of delayed transactions
SELECT
    COUNT(*) AS delayed_transactions
FROM transactions
WHERE status = 'PENDING'
AND NOW() - created_at >= INTERVAL '10 seconds';

--Overall failure rate
SELECT
    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE status = 'FAILED'
    ) AS failed_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE status = 'FAILED'
        )::NUMERIC
        / COUNT(*) * 100,
        2
    ) AS failure_rate
FROM transactions;

--Merchant performance
SELECT
    m.merchant_id,
    m.name AS merchant,

    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE t.status = 'FAILED'
    ) AS failed_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE t.status = 'FAILED'
        )::NUMERIC
        / COUNT(*) * 100,
        2
    ) AS failure_rate

FROM transactions t

JOIN merchants m
    ON t.merchant_id = m.merchant_id

GROUP BY m.merchant_id, m.name

ORDER BY failure_rate DESC;

--Payment-method performance
SELECT
    pm.payment_method_id,
    pm.method_name,

    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE t.status = 'FAILED'
    ) AS failed_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE t.status = 'FAILED'
        )::NUMERIC
        / COUNT(*) * 100,
        2
    ) AS failure_rate

FROM transactions t

LEFT JOIN payment_methods pm
    ON pm.payment_method_id = t.payment_method_id

GROUP BY pm.payment_method_id, pm.method_name

ORDER BY failure_rate DESC;

--Customer spending
SELECT
    c.customer_id,
    c.name AS customer,

    SUM(t.amount) AS total_spend,

    COUNT(*) AS total_transactions

FROM transactions t

JOIN customers c
    ON t.customer_id = c.customer_id

GROUP BY c.customer_id, c.name

ORDER BY total_spend DESC;

--Customer failure rate
SELECT
    c.customer_id,
    c.name AS customer,

    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE t.status = 'FAILED'
    ) AS failed_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE t.status = 'FAILED'
        )::NUMERIC
        / COUNT(*) * 100,
        2
    ) AS failure_rate

FROM transactions t

JOIN customers c
    ON t.customer_id = c.customer_id

GROUP BY c.customer_id, c.name

ORDER BY failure_rate DESC;

--Pending health
SELECT
    CASE
        WHEN NOW() - created_at >= INTERVAL '10 seconds'
        THEN 'DELAYED'
        ELSE 'NORMAL'
    END AS status_type,

    COUNT(*) AS transaction_count

FROM transactions

WHERE status = 'PENDING'

GROUP BY
    CASE
        WHEN NOW() - created_at >= INTERVAL '10 seconds'
        THEN 'DELAYED'
        ELSE 'NORMAL'
    END;

--Hourly transactions
SELECT
    EXTRACT(HOUR FROM created_at) AS hour,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY EXTRACT(HOUR FROM created_at)
ORDER BY hour;

--success rate
SELECT
    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE status = 'SUCCESS'
    ) AS successful_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE status = 'SUCCESS'
        )::NUMERIC
        / COUNT(*) * 100,
        2
    ) AS success_rate

FROM transactions;

--Daily failure rate
SELECT
    DATE(created_at) AS transaction_date,

    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE status = 'FAILED'
    ) AS failed_transactions,

    ROUND(
        COUNT(*) FILTER (
            WHERE status = 'FAILED'
        )::NUMERIC
        / COUNT(*) * 100,
        2
    ) AS failure_rate

FROM transactions

GROUP BY DATE(created_at)

ORDER BY transaction_date;

--Daily revenue
SELECT
    DATE(created_at) AS transaction_date,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_value
FROM transactions
GROUP BY DATE(created_at)
ORDER BY transaction_date;

--Final dashboard KPI query
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
        / COUNT(*) * 100,
        2
    ) AS success_rate,

    ROUND(SUM(amount), 2) AS total_transaction_value

FROM transactions;

--Top delayed transactions

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