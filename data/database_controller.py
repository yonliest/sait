import json
import psycopg2

def connection_string():
    conn_str = {}
    with open("data/db_config.json", "r", encoding='utf-8') as file:
        conn_str = json.load(file)

    return conn_str