# Dataset: https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-electronics-store

from urllib.parse import quote_plus

import polars as pl
from pymongo import MongoClient

MONGO_SERVICE_DOMAIN = "mongo"
MONGO_SERVICE_PORT = 27017

MONGO_USER = "mongo"
MONGO_PASS = "mongo"

MONGO_DB = "data_playground"
MONGO_COLLECTION = "user_events"

BATCH_ITER_NUM = 1


def connect_to_mongo(db_name, coll_name):
    client = MongoClient(
        f"mongodb://{quote_plus(MONGO_USER)}:{quote_plus(MONGO_PASS)}@{MONGO_SERVICE_DOMAIN}",
        MONGO_SERVICE_PORT,
    )
    db = client[db_name]
    return db[coll_name]


def stream_data_from_csv(csv_file_path):
    return pl.read_csv_batched(csv_file_path)


def stream_csv_to_mongo(csv_file_path, db_name, coll_name):
    collection = connect_to_mongo(db_name, coll_name)
    batch_reader = pl.read_csv_batched(csv_file_path)
    batch_list = batch_reader.next_batches(BATCH_ITER_NUM)
    while batch_list is not None:
        for batch in batch_list:
            converted_batch = batch.with_columns(
                batch["event_time"]
                .str.to_datetime("%Y-%m-%d %H:%M:%S %Z")
                .alias("event_time"),
            )
            collection.insert_many(converted_batch.to_dicts())
        batch_list = batch_reader.next_batches(BATCH_ITER_NUM)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    input_csv_dir = Path(sys.argv[1])
    csv_files = [
        item.absolute()
        for item in input_csv_dir.iterdir()
        if item.is_file() and item.name.endswith(".csv")
    ]
    mongo_collection = sys.argv[2] if len(sys.argv) > 2 else MONGO_COLLECTION
    for file in csv_files:
        stream_csv_to_mongo(file, MONGO_DB, mongo_collection)
