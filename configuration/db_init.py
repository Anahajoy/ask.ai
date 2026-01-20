from pathlib import Path
from .db import get_connection


DB_NAME = "dbs"
SCHEMA_VERSION = 1
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def schema_applied(cursor) -> bool:
    """Check if the schema has been applied"""
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM dbo.schema_version 
            WHERE version = ?
        """, SCHEMA_VERSION)
        return cursor.fetchone()[0] > 0
    except:
        # Table doesn't exist yet
        return False


def apply_schema(cursor):
    """Apply the schema from schema.sql"""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    print(f"Executing schema script...\n")

    try:
        cursor.execute(sql_script)
        print(f"✅ Schema executed successfully\n")
        
    except Exception as e:
        print(f"\n❌ Error executing schema: {e}")
        raise

    # Record schema version
    cursor.execute(
        "INSERT INTO dbo.schema_version (version) VALUES (?)",
        SCHEMA_VERSION
    )
    
    print(f"✅ Schema version {SCHEMA_VERSION} applied successfully")


def initialize_database():
    """Initialize the database schema (assumes database 'dbs' already exists)"""
    try:
        print("=" * 50)
        print("Initializing Database Schema")
        print("=" * 50)
        
        conn = get_connection(DB_NAME)
        cursor = conn.cursor()
        
        try:
            if not schema_applied(cursor):
                print("📝 Applying schema for the first time...\n")
                apply_schema(cursor)
                conn.commit()
                print("\n✅ Schema applied and committed successfully")
            else:
                print("ℹ️ Schema already applied - skipping")
        
        finally:
            cursor.close()
            conn.close()
        
        print("=" * 50)
        print("✅ Database initialization complete!")
        print("=" * 50)
            
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        raise