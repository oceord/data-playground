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
SCHEMA = "public"
TABLENAME = "events"

SEP = ","


def drop_create_database():
    conn = psycopg2.connect(host=HOST, user=USER, password=PASSWORD)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        print(f"Dropping '{DBNAME}'")
        drop_db_query = sql.SQL("DROP DATABASE IF EXISTS {}").format(
            sql.Identifier(DBNAME),
        )
        cur.execute(drop_db_query)
        print(f"Creating '{DBNAME}'")
        create_db_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DBNAME))
        cur.execute(create_db_query)
    finally:
        cur.close()
        conn.close()


def ingest_data(file):
    print(f"Ingesting {file}")
    with psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DBNAME,
    ) as conn, conn.cursor() as cur:
        print(f"Creating table {SCHEMA}.{TABLENAME} if not exists")
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
        ).format(sql.Identifier(SCHEMA, TABLENAME))
        cur.execute(create_table_query)
        print(f"Copying data from {file} to {SCHEMA}.{TABLENAME}")
        with file.open("r") as f:
            next(f)  # skip header
            cur.copy_from(f, TABLENAME, SEP)
        query = sql.SQL("SELECT count(1) FROM {}").format(
            sql.Identifier(SCHEMA, TABLENAME),
        )
        cur.execute(query)
        res = cur.fetchall()
        print(*res, sep="\n")


if __name__ == "__main__":
    import sys

    input_csvs = [Path(p) for p in sys.argv[1:]]
    drop_create_database()
    for input_csv in input_csvs:
        ingest_data(input_csv)
