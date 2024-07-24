import csv

from neo4j import GraphDatabase

URI = "neo4j://neo4j"


def ingest_data(file):
    driver = GraphDatabase.driver(URI)
    with file.open(mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row_dict in reader:
            ingest_category(driver, row_dict)
            ingest_seller(driver, row_dict)
            ingest_product(driver, row_dict)


def ingest_category(driver, row_dict):
    raise NotImplementedError
    create_cat_query = "CREATE (n:NodeExample {name: $name, uuid: randomUUID()})"
    cat_name = "CAT_NAME"
    run_query(driver, create_cat_query, name=cat_name)
    create_subcategory_query = (
        "CREATE (n:NodeExample {name: $name, uuid: randomUUID()})"
    )
    subcat_name = "SUBCAT_NAME"
    run_query(driver, create_subcategory_query, name=subcat_name)


def ingest_seller(driver, row_dict):
    raise NotImplementedError
    create_seller_query = "CREATE (n:NodeExample {name: $name, uuid: randomUUID()})"
    seller_name = "SELLER_NAME"
    run_query(driver, create_seller_query, name=seller_name)


def ingest_product(driver, row_dict):
    raise NotImplementedError
    create_prod_query = "CREATE (n:NodeExample {name: $name, uuid: randomUUID()})"
    prod_name = "PRODUCT_NAME"
    run_query(driver, create_prod_query, name=prod_name)
    create_relation_query = (
        "MATCH "
        "(a:NodeExample {name: $node_a_name}), "
        "(b:NodeExample {name: $node_b_name}) "
        "MERGE (a)-[:related_to]->(b)"
    )
    node_a_name = "PRODUCT_NAME"
    node_b_name = "CAT_NAME"
    run_query(
        driver,
        create_relation_query,
        node_a_name=node_a_name,
        node_b_name=node_b_name,
    )


def run_query(driver, query, /, **kwargs):
    with driver.session() as session:
        session.execute_write(tx_function, query, kwargs)


def tx_function(tx, query, kwargs):
    tx.run(query, **kwargs)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    input_csv = Path(sys.argv[1])
    ingest_data(input_csv)
