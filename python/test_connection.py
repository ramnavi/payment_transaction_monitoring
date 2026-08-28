import psycopg2
from config import DB_CONFIG

try:
    connection = psycopg2.connect(**DB_CONFIG)

    print("Database connection successful!")

    connection.close()

except Exception as error:
    print("Database connection failed:")
    print(error)