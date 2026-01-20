import pyodbc
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def get_connection(database_override=None, autocommit=False):
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    db = config["database"]
    database = database_override or db["database"]

    conn_str = (
        f"DRIVER={{{db['driver']}}};"
        f"SERVER={db['server']};"
        f"DATABASE={database};"
    )

    if db.get("trusted_connection", "").lower() == "yes":
        conn_str += "Trusted_Connection=yes;"
    else:
        conn_str += f"UID={db['username']};PWD={db['password']};"

    if db.get("trust_server_certificate", "").lower() == "yes":
        conn_str += "TrustServerCertificate=yes;"

    conn = pyodbc.connect(conn_str)
    conn.autocommit = autocommit
    
    return conn