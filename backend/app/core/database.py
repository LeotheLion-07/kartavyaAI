from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def sync_database_schema(target_engine=None):
    """
    Safely inspects existing database schema and performs idempotent ALTER TABLE
    migrations to guarantee zero data loss and forward compatibility for added columns.
    Works for both SQLite and PostgreSQL.
    """
    eng = target_engine or engine
    inspector = inspect(eng)
    existing_tables = inspector.get_table_names()

    migrations = {
        "conflicts": [
            ("category", "VARCHAR(100)", "'Ownership'"),
            ("entity_or_subject", "VARCHAR(255)", "NULL"),
            ("detection_reason", "TEXT", "NULL"),
            ("source_a_value", "VARCHAR(255)", "NULL"),
            ("source_b_value", "VARCHAR(255)", "NULL"),
            ("access_classification", "VARCHAR(50)", "'Team'"),
        ],
        "knowledge_gap_questions": [
            ("category", "VARCHAR(100)", "'DecisionRationale'"),
            ("entity_or_subject", "VARCHAR(255)", "NULL"),
            ("priority", "VARCHAR(50)", "'High'"),
            ("source_id", "INTEGER", "NULL"),
        ],
        "claims": [
            ("entity_or_subject", "VARCHAR(255)", "NULL"),
            ("extracted_value", "VARCHAR(255)", "NULL"),
        ],
        "source_chunks": [
            ("access_classification", "VARCHAR(50)", "'Team'"),
        ],
    }

    with eng.connect() as conn:
        for table, columns in migrations.items():
            if table in existing_tables:
                existing_cols = {col["name"] for col in inspector.get_columns(table)}
                for col_name, col_type, default_val in columns:
                    if col_name not in existing_cols:
                        try:
                            if is_sqlite:
                                sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type} DEFAULT {default_val}"
                            else:
                                sql = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col_name} {col_type} DEFAULT {default_val}"
                            conn.execute(text(sql))
                            conn.commit()
                        except Exception as ex:
                            # Log or ignore if already added concurrently
                            pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
