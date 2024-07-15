import time
import random
import datetime

import pytz
import psycopg2

create_table_statement = """
CREATE TABLE if not exists dummy_metrics(
    timestamp timestamp,
    numeric_val float
);

"""


def init_table():
    with psycopg2.connect(
        "host=localhost port=5432 user=monitoring password=secret dbname=monitoring",
    ) as conn:

        with conn.cursor() as curr:
            curr.execute(create_table_statement)


def add_dummy_data():
    insert_statement = "INSERT INTO dummy_metrics(timestamp, numeric_val) VALUES(%s, %s);"
    timestamp = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    with psycopg2.connect(
        "host=localhost port=5432 user=monitoring password=secret dbname=monitoring",
    ) as conn:
        with conn.cursor() as curr:

            curr.execute(
                insert_statement,
                (timestamp, random.random() * 100),
            )


if __name__ == "__main__":
    init_table()
    while True:
        add_dummy_data()
        time.sleep(4)
