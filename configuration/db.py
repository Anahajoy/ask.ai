import pyodbc
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"

def get_connection():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    db = config["database"]

    conn_str = (
        f"DRIVER={{{db['driver']}}};"
        f"SERVER={db['server']};"
        f"DATABASE={db['database']};"
    )

    if db.get("trusted_connection", "").lower() == "yes":
        conn_str += "Trusted_Connection=yes;"
    else:
        conn_str += f"UID={db['username']};PWD={db['password']};"

    if db.get("trust_server_certificate", "").lower() == "yes":
        conn_str += "TrustServerCertificate=yes;"

    return pyodbc.connect(conn_str)
