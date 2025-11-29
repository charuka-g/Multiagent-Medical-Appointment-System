import psycopg2
import os
from dotenv import load_dotenv


def connect_to_db():
    """
    Creates and returns a connection to Supabase PostgreSQL.
    Reads credentials from environment variables.
    """
    load_dotenv()

    return psycopg2.connect(
        host=os.getenv("POSTGRE_HOST"),
        database=os.getenv("POSTGRE_DB_NAME"),
        user=os.getenv("POSTGRE_DB_USER"),
        password=os.getenv("POSTGRE_PASSWORD"),
        port=os.getenv("POSTGRE_PORT")
    )
