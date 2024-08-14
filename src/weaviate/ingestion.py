# Datasets:
#   https://www.kaggle.com/datasets/saurabhshahane/ecommerce-text-classification

import csv

import weaviate

HOST = "weaviate"
PORT = 8080


def ingest_data(file):
    client = weaviate.connect_to_local(host=HOST, port=PORT)
    if not client.is_ready():
        msg = "Weaviate client is not ready"
        raise ConnectionError(msg)
    with file.open(mode="r") as csv_file:
        reader = csv.reader(csv_file)
        raise NotImplementedError


if __name__ == "__main__":
    import sys
    from pathlib import Path

    input_csv = Path(sys.argv[1])
    ingest_data(input_csv)
