"""
Offline SQLite Database Connection & Session Management for KrishiDrishti Edge.
Enforces foreign key constraints in SQLite via PRAGMA.
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.logging import log_event

# Ensure parent directory for SQLite file exists
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    db_path = db_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

# Create engine (check_same_thread=False is required for SQLite with multi-threaded FastAPI)
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    echo=False
)

# Enforce SQLite foreign key constraints
if db_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency yielding a transactional DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Safe database initialization.
    Creates all missing tables without destroying existing data.
    """
    from app.db import models  # Ensure all models are registered with Base
    Base.metadata.create_all(bind=engine)
    log_event("DATABASE", "INFO", f"SQLite tables initialized from {settings.DATABASE_URL}")
