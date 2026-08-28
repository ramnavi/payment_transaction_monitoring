import random
import time
import psycopg2
from config import DB_CONFIG


# Connect to PostgreSQL
connection = psycopg2.connect(**DB_CONFIG)
cursor = connection.cursor()


while True:

    # Generate random transaction data
    customer_id = random.randint(1, 10)
    merchant_id = random.randint(1, 5)
    payment_method_id = random.randint(1, 5)

    amount = round(random.uniform(100, 50000), 2)

    status = random.choices(
        ["SUCCESS", "FAILED", "PENDING", "CANCELLED"],
        weights=[90, 5, 3, 2],
        k=1
    )[0]

    # Insert transaction
    query = """
INSERT INTO transactions
(
    customer_id,
    merchant_id,
    payment_method_id,
    amount,
    status,
    created_at,
    completed_at
)
VALUES (
    %s,
    %s,
    %s,
    %s,
    %s,
    NOW(),
    CASE
        WHEN %s = 'PENDING' THEN NULL
        ELSE NOW()
    END
)
RETURNING transaction_id;
"""

    cursor.execute(
    query,
    (
        customer_id,
        merchant_id,
        payment_method_id,
        amount,
        status,
        status
    )
)

    transaction_id = cursor.fetchone()[0]

    connection.commit()

    print(f"Transaction created: {transaction_id}")
    print(f"Customer: {customer_id}")
    print(f"Merchant: {merchant_id}")
    print(f"Amount: ₹{amount}")
    print(f"Status: {status}")
    print("-" * 40)

    # Wait 2 seconds before generating the next transaction
    time.sleep(2)