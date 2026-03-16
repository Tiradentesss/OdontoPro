import os
import mysql.connector
from config.settings import DB_CONFIG


def get_connection():
    ssl_ca = DB_CONFIG.get("ssl_ca")

    if ssl_ca and not os.path.isabs(ssl_ca):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        ssl_ca = os.path.join(base_dir, ssl_ca)

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=DB_CONFIG["port"],
        ssl_ca=ssl_ca
    )
