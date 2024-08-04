# Dataset: https://www.kaggle.com/datasets/aaditshukla/flipkart-fasion-products-dataset

import ast
import csv
from datetime import datetime, timezone

from elasticsearch import Elasticsearch, helpers

ES_URL = "http://elasticsearch:9200"
INDEX = "data_playground_products"


def ingest_data(file):
    es = Elasticsearch(hosts=[ES_URL])
    clear(es)
    rows_dict_iter = row_iter(file)
    ingest_product(es, rows_dict_iter)


def clear(es):
    es.options(ignore_status=[400, 404]).indices.delete(index=INDEX)


def ingest_product(es, docs):
    helpers.bulk(es, docs)


def row_iter(file):
    with file.open(mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row_dict in reader:
            yield {
                "_index": INDEX,
                "_source": parse_row_dict(row_dict),
            }


def parse_row_dict(row_dict):
    row_dict.pop("")
    row_dict["uid"] = row_dict.pop("_id")
    row_dict = parse_float(row_dict, "actual_price")
    row_dict = parse_float(row_dict, "average_rating")
    row_dict["crawled_at"] = datetime.strptime(
        row_dict["crawled_at"],
        "%m/%d/%Y, %H:%M:%S",
    ).replace(tzinfo=timezone.utc)
    discount_split = row_dict["discount"].split("%") if row_dict["discount"] else None
    row_dict["discount"] = float(discount_split[0]) if discount_split else 0
    row_dict["images"] = ast.literal_eval(row_dict["images"])
    row_dict["out_of_stock"] = row_dict["out_of_stock"] == "TRUE"
    row_dict["product_details"] = {
        k: v
        for d in ast.literal_eval(row_dict["product_details"])
        for k, v in d.items()
        if k.strip() != ""
    }
    return parse_float(row_dict, "selling_price")


def parse_float(row_dict, key):
    if row_dict[key]:
        row_dict[key] = float(row_dict[key].replace(",", ""))
    else:
        row_dict.pop(key)
    return row_dict


if __name__ == "__main__":
    import sys
    from pathlib import Path

    input_csv = Path(sys.argv[1])
    ingest_data(input_csv)
