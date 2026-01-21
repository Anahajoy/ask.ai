import pymssql
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def get_connection(database_override=None, autocommit=False):
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    db = config["database"]
    database = database_override or db["database"]

    # Check if using Windows Authentication
    if db.get("trusted_connection", "").lower() == "yes":
        # pymssql doesn't support Windows Authentication on Linux/Streamlit Cloud
        raise NotImplementedError(
            "Windows Authentication (Trusted_Connection) is not supported on Streamlit Cloud. "
            "Please use SQL Server Authentication with username/password."
        )
    
    conn = pymssql.connect(
        server=db['server'],
        database=database,
        user=db['username'],
        password=db['password'],
        tds_version='7.0'  # Or '7.4' for newer SQL Server versions
    )
    
    conn.autocommit = autocommit
    
    return conn