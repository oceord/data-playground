# Dataset: https://www.kaggle.com/datasets/saurabhshahane/ecommerce-text-classification

import csv

import pandas as pd
import weaviate
from weaviate.classes.config import Configure, DataType, Property, ReferenceProperty

HOST = "weaviate"
PORT = 8080
CAT_COLLECTION = "DataPlayground_Categories"
CAT_SCHEMA_CONFIG = {
    "name": CAT_COLLECTION,
    "vectorizer_config": None,
    "properties": [
        Property(name="name", data_type=DataType.TEXT),
    ],
}

COLLECTION = "DataPlayground_Products"
SCHEMA_CONFIG = {
    "name": COLLECTION,
    "vectorizer_config": Configure.Vectorizer.text2vec_transformers(),
    "properties": [
        Property(name="description", data_type=DataType.TEXT),
        Property(
            name="category",
            data_type=DataType.TEXT,
            skip_vectorization=True,  # Don't vectorize this property
        ),
    ],
    "references": [
        ReferenceProperty(
            name="classifiedCategory",
            target_collection=CAT_COLLECTION,
        ),
    ],
}


def ingest_data(file):
    with weaviate.connect_to_local(host=HOST, port=PORT) as client:
        _check_weaviate(client)
        client.collections.delete_all()
        ingest_categories(client, file)
        with file.open(mode="r") as csv_file:
            reader = csv.reader(csv_file)
            collection = client.collections.create(**SCHEMA_CONFIG)
            with collection.batch.dynamic() as batch:
                for category, description in reader:
                    batch.add_object(
                        properties={
                            "category": category,
                            "description": description,
                        },
                    )


def _check_weaviate(client):
    if not client.is_ready():
        msg = "Weaviate client is not ready"
        raise ConnectionError(msg)


def ingest_categories(client, file):
    collection = client.collections.create(**CAT_SCHEMA_CONFIG)
    categories = set(
        pd.read_csv(
            file,
            sep=",",
            header=None,
            dtype="str",
            usecols=[0],
            index_col=None,
        ).to_dict("list")[0],
    )
    for cat in categories:
        collection.data.insert({"name": cat})


if __name__ == "__main__":
    import sys
    from pathlib import Path

    input_csv = Path(sys.argv[1])
    ingest_data(input_csv)
