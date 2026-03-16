import os
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": "odontoplace-odontopro2-87cf.f.aivencloud.com",
    "user": "avnadmin",
    "password": os.getenv("DB_PASSWORD"),
    "database": "defaultdb",
    "port": 23912,
    "ssl_ca": "config/ca.pem"
}
