import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase Database connection details
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def fetch_value_from_supabase(sql_query):
    """Fetch `kgco2e` value from Supabase."""
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchone()  # Fetch only one value

        cursor.close()
        conn.close()

        if result:
            return float(result[0])  # Convert to float
        return None

    except Exception as e:
        print("Database Error:", e)
        return None
