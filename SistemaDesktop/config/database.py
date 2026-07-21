import os
import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
from config.settings import DB_CONFIG

# Simple connection pool singleton
_POOL = None

def _init_pool_if_needed():
    global _POOL
    if _POOL is not None:
        return

    pool_size = int(DB_CONFIG.get('pool_size', 5))
    ssl_ca = DB_CONFIG.get('ssl_ca')
    if ssl_ca and not os.path.isabs(ssl_ca):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        ssl_ca = os.path.join(base_dir, ssl_ca)

    connection_params = {
        'host': DB_CONFIG['host'],
        'user': DB_CONFIG['user'],
        'password': DB_CONFIG.get('password', ''),
        'database': DB_CONFIG['database'],
        'port': DB_CONFIG.get('port', 3306),
        'connection_timeout': int(DB_CONFIG.get('connect_timeout', 30)),
        'auth_plugin': DB_CONFIG.get('auth_plugin', 'mysql_native_password'),
        'use_unicode': True,
        'charset': 'utf8mb4'
    }

    if ssl_ca and os.path.exists(ssl_ca):
        connection_params['ssl_ca'] = ssl_ca

    # Create pool
    try:
        _POOL = pooling.MySQLConnectionPool(pool_name='odontopro_pool', pool_size=pool_size, **connection_params)
    except Exception as e:
        raise ConnectionError(f"Não foi possível criar o pool de conexões: {e}") from e


def get_connection():
    """Return a connection from the pool. Closing the connection will return it to the pool.

    Keeps the same API as before: callers must close() the connection when done.
    """
    global _POOL
    if _POOL is None:
        _init_pool_if_needed()

    try:
        return _POOL.get_connection()
    except Error as err:
        raise ConnectionError(f"Não foi possível obter conexão do pool: {err}") from err
