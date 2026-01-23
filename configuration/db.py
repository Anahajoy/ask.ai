import pyodbc
import streamlit as st


def get_connection(database_override=None, autocommit=False):
    database = database_override or st.secrets["DB_NAME"]

    conn_str = (
        f"DRIVER={{{st.secrets['DB_DRIVER']}}};"
        f"SERVER={st.secrets['DB_SERVER']};"
        f"DATABASE={database};"
    )

    if st.secrets.get("DB_TRUSTED_CONNECTION", "").lower() == "yes":
        conn_str += "Trusted_Connection=yes;"
    else:
        conn_str += (
            f"UID={st.secrets['DB_USERNAME']};"
            f"PWD={st.secrets['DB_PASSWORD']};"
        )

    if st.secrets.get("DB_TRUST_SERVER_CERTIFICATE", "").lower() == "yes":
        conn_str += "TrustServerCertificate=yes;"

    conn = pyodbc.connect(conn_str)
    conn.autocommit = autocommit
    return conn
