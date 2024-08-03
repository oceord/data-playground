from elasticsearch import Elasticsearch


def ingest_data(file):
    es = Elasticsearch(hosts=["http://elasticsearch:9200"])
    raise NotImplementedError


if __name__ == "__main__":
    import sys
    from pathlib import Path

    input_csv = Path(sys.argv[1])
    ingest_data(input_csv)
