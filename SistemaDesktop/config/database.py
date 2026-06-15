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
        connection_params = {
            "host": DB_CONFIG["host"],
            "user": DB_CONFIG["user"],
            "password": DB_CONFIG.get("password", ""),
            "database": DB_CONFIG["database"],
            "port": DB_CONFIG.get("port", 3306),
            "connection_timeout": int(DB_CONFIG.get("connect_timeout", 30)),
            "auth_plugin": DB_CONFIG.get("auth_plugin", "mysql_native_password"),
            "autocommit": True,
            "use_unicode": True,
            "charset": "utf8mb4"
        }
        
        # Adicionar SSL se configurado
        if ssl_ca and os.path.exists(ssl_ca):
            connection_params["ssl_ca"] = ssl_ca

        return mysql.connector.connect(**connection_params)
    except Error as err:
        raise ConnectionError(f"Não foi possível conectar ao banco: {err}") from err
