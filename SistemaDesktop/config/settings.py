import os
from dotenv import load_dotenv
load_dotenv()

# Banco de dados Online (Aiven):

DB_CONFIG = {
    "host": "odontoplace-odontopro2-87cf.f.aivencloud.com",
    "user": "avnadmin",
    "password": os.getenv("DB_PASSWORD"),
    "database": "defaultdb",
    "port": 23912,
    "ssl_ca": "config/ca.pem",
    "auth_plugin": "mysql_native_password"
}

# Banco de dados Local (comentado):
# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database": "odontoprodb",
#     "port": 3306
# }
