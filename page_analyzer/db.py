import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


class Repository:

    def find_by_id(self, id):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM urls WHERE id = %s;",
                    (id,)
                )
                return cur.fetchone()

    def find_by_name(self, name):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM urls WHERE name = %s;",
                    (name,)
                )
                return cur.fetchone()

    def all_posts(self):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM urls ORDER BY created_at DESC;"
                )
                return cur.fetchall()

    def save(self, url):
        if self.find_by_name(url):
            return False

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO urls (name) 
                    VALUES (%s) 
                    RETURNING id;
                    """,
                    (url,)
                )
                result = cur.fetchone()
                return result['id']