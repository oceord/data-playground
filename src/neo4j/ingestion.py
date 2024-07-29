import csv

from neo4j import GraphDatabase

URI = "neo4j://neo4j"


def ingest_data(file):
    driver = GraphDatabase.driver(URI)
    clear(driver)
    with file.open(mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row_dict in reader:
            ingest_category(driver, row_dict)
            ingest_seller(driver, row_dict)
            ingest_product(driver, row_dict)


def clear(driver):
    query = "MATCH (n) DETACH DELETE n"
    run_query(driver, query)


def ingest_category(driver, row_dict):
    create_cat_query = "MERGE (c:Category {name: $name})"
    cat_name = row_dict.get("category")
    run_query(driver, create_cat_query, name=cat_name)
    create_subcategory_query = "MERGE (sc:SubCategory {name: $name})"
    subcat_name = row_dict.get("sub_category")
    run_query(driver, create_subcategory_query, name=subcat_name)
    relate_cat_to_sub_cat_query = (
        "MATCH "
        "(c:Category {name: $node_a_name}), "
        "(sc:SubCategory {name: $node_b_name}) "
        "MERGE (sc)-[:SUBCATEGORY_OF]->(c)"
    )
    run_query(
        driver,
        relate_cat_to_sub_cat_query,
        node_a_name=cat_name,
        node_b_name=subcat_name,
    )


def ingest_seller(driver, row_dict):
    create_seller_query = "MERGE (s:Seller {name: $name})"
    seller_name = row_dict.get("seller")
    run_query(driver, create_seller_query, name=seller_name)


def ingest_product(driver, row_dict):
    create_prod_query = """
        MERGE (newProduct:Product {pid: $prod_pid})
        ON CREATE SET
            newProduct.name = $name,
            newProduct.desc = $prod_desc,
            newProduct.brand = $prod_brand,
            newProduct.price = $prod_price,
            newProduct.url = $prod_url,
            newProduct.avg_rating = $prod_rating
    """
    prod_name = row_dict.get("title")
    prod_desc = row_dict.get("description")
    prod_pid = row_dict.get("pid")
    prod_brand = row_dict.get("brand") or None
    prod_url = row_dict.get("url") or None
    prod_price = cast(row_dict.get("actual_price").replace(",", ""), float)
    prod_rating = cast(row_dict.get("average_rating").replace(",", ""), float)
    run_query(
        driver,
        create_prod_query,
        prod_pid=prod_pid,
        name=prod_name,
        prod_desc=prod_desc,
        prod_brand=prod_brand,
        prod_url=prod_url,
        prod_price=prod_price,
        prod_rating=prod_rating,
    )
    # create_cat_rel_query = """
    #     MATCH
    #     (p:Product {name: $product_name}),
    #     (c:Category {name: $category_name})
    #     MERGE (p)-[:HAS_CATEGORY]->(c)
    # """
    # category_name = row_dict.get("category")
    # run_query(
    #     driver,
    #     create_cat_rel_query,
    #     product_name=prod_name,
    #     category_name=category_name,
    # )
    create_subcat_rel_query = """
        MATCH
        (p:Product {pid: $prod_pid}),
        (sc:SubCategory {name: $category_name})
        MERGE (p)-[:HAS_CATEGORY]->(sc)
    """
    subcategory_name = row_dict.get("sub_category")
    run_query(
        driver,
        create_subcat_rel_query,
        prod_pid=prod_pid,
        category_name=subcategory_name,
    )
    create_seller_rel_query = """
        MATCH
        (p:Product {pid: $prod_pid}),
        (s:Seller {name: $seller})
        MERGE (s)-[r:SELLS]->(p)
        ON CREATE SET
            r.selling_price = $selling_price,
            r.out_of_stock = $out_of_stock,
            r.discount = $discount
    """
    seller_name = row_dict.get("seller")
    selling_price = cast(row_dict.get("selling_price").replace(",", ""), float)
    out_of_stock = row_dict.get("out_of_stock") == "TRUE"
    discount_str = row_dict.get("discount")
    discount_split = discount_str.split("%")
    discount = cast(discount_split[0] if discount_split else 0, float)
    run_query(
        driver,
        create_seller_rel_query,
        seller=seller_name,
        prod_pid=prod_pid,
        selling_price=selling_price,
        out_of_stock=out_of_stock,
        discount=discount,
    )


def cast(field_str, typ):
    return typ(field_str) if field_str else None


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
