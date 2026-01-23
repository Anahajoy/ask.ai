import psycopg2
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=int(st.secrets.get("DB_PORT", 5432)),
        sslmode="require"
    )


def init_db():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"schema.sql not found at {SCHEMA_PATH}")

    sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(sql)

    print("✅ Database initialized successfully")
