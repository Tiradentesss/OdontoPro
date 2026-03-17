import os
import mysql.connector
from mysql.connector import Error
from config.settings import DB_CONFIG


def get_connection():
    ssl_ca = DB_CONFIG.get("ssl_ca")

    if ssl_ca and not os.path.isabs(ssl_ca):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        ssl_ca = os.path.join(base_dir, ssl_ca)

    try:
        return mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG.get("password", ""),
            database=DB_CONFIG["database"],
            port=DB_CONFIG.get("port", 3306),
            ssl_ca=ssl_ca,
            connection_timeout=int(DB_CONFIG.get("connect_timeout", 5)),
            auth_plugin=DB_CONFIG.get("auth_plugin", "mysql_native_password")
        )
    except Error as err:
        raise ConnectionError(f"Não foi possível conectar ao banco: {err}") from err
