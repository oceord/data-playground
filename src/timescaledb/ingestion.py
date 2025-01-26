# Datasets:
#   https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-electronics-store
#   https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store

from pathlib import Path

import psycopg2
from psycopg2 import sql

HOST = "timescaledb"
PORT = 5432
USER = "timescaledb"
PASSWORD = "timescaledb"

DBNAME = "db_user_events"
TABLENAME = "t_user_events"

SEP = ","


def reset_db_structures():
    drop_create_db()
    create_table()


def drop_create_db():
    conn = psycopg2.connect(host=HOST, user=USER, password=PASSWORD)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        print(f"Dropping db '{DBNAME}'")
        drop_db_query = sql.SQL("DROP DATABASE IF EXISTS {}").format(
            sql.Identifier(DBNAME),
        )
        cur.execute(drop_db_query)
        print(f"Creating db '{DBNAME}'")
        create_db_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DBNAME))
        cur.execute(create_db_query)
    except Exception:
        cur.close()
        conn.close()
        raise
    finally:
        cur.close()
        conn.close()


def create_table():
    with psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DBNAME,
    ) as conn, conn.cursor() as cur:
        print(f"Creating table '{TABLENAME}'")
        create_table_query = sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {} (
                event_time TIMESTAMPTZ,
                event_type VARCHAR(100),
                product_id INT,
                category_id BIGINT,
                category_code VARCHAR(100),
                brand VARCHAR(100),
                price NUMERIC,
                user_id BIGINT,
                user_session VARCHAR(100)
            );
        """,
        ).format(sql.Identifier(TABLENAME))
        cur.execute(create_table_query)


def ingest_data_file(file):
    with psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DBNAME,
    ) as conn, conn.cursor() as cur:
        print(f"Copying data from {file} to table '{TABLENAME}'")
        with file.open("r") as f:
            next(f)  # skip header
            cur.copy_from(f, TABLENAME, SEP)
        query = sql.SQL("SELECT count(1) FROM {}").format(
            sql.Identifier(TABLENAME),
        )
        cur.execute(query)
        res = cur.fetchone()[0]
        print(f"Copied {res:_} items into '{TABLENAME}'")


def ingest_data_files(input_csvs):
    for input_csv in input_csvs:
        ingest_data_file(input_csv)


if __name__ == "__main__":
    import sys

    input_csvs = [Path(p) for p in sys.argv[1:]]
    ingest_data_files(input_csvs)
