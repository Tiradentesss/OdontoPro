import os
from dotenv import load_dotenv

load_dotenv()

# Construir configuração do banco a partir de variáveis de ambiente
# Isso permite alternar facilmente entre DB local e Aiven/remoto sem editar o código.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "odontoprodb")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_SSL_CA = os.getenv("DB_SSL_CA", "config/ca.pem")

# Se o host remoto padrão do Aiven for usado e houver senha, aplicar porta/DB específicos
if DB_HOST and DB_HOST != "localhost":
    DB_CONFIG = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": os.getenv("DB_NAME", "defaultdb"),
        "port": int(os.getenv("DB_PORT", 23912)),
        "ssl_ca": DB_SSL_CA if DB_SSL_CA else None,
        "auth_plugin": os.getenv("DB_AUTH_PLUGIN", "mysql_native_password")
    }
else:
    # Configuração local padrão (WAMP/XAMPP)
    DB_CONFIG = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME,
        "port": DB_PORT
    }
