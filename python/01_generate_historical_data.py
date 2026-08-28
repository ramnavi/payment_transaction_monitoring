import random
from datetime import datetime, timedelta
import psycopg2
from config import DB_CONFIG


# Connect to PostgreSQL
connection = psycopg2.connect(**DB_CONFIG)
cursor = connection.cursor()


# Generate 7 days of historical transactions
for _ in range(200):

    # Random timestamp from the last 7 days
    created_at = datetime.now() - timedelta(
        days=random.randint(0, 6),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

    customer_id = random.randint(1, 10)
    merchant_id = random.randint(1, 5)
    payment_method_id = random.randint(1, 5)

    amount = round(random.uniform(100, 50000), 2)

    status = random.choices(
        ["SUCCESS", "FAILED", "PENDING", "CANCELLED"],
        weights=[90, 5, 3, 2],
        k=1
    )[0]

    # Pending transactions have no completion time
    completed_at = None if status == "PENDING" else created_at

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
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    cursor.execute(
        query,
        (
            customer_id,
            merchant_id,
            payment_method_id,
            amount,
            status,
            created_at,
            completed_at
        )
    )


connection.commit()

print("200 historical transactions created successfully.")

cursor.close()
connection.close()