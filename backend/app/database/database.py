# database/database.py
# SQLAlchemy 2.0 database configuration for DocMind AI.
#
# This module provides three shared objects used throughout the application:
#   engine        — the connection pool to PostgreSQL
#   SessionLocal  — the factory that produces per-request database sessions
#   Base          — the ORM declarative base all models inherit from
#
# It also provides get_db(), a FastAPI dependency that opens a session,
# yields it to the route handler, and always closes it when the request ends.

from typing import Generator

# create_engine builds the connection pool.
from sqlalchemy import create_engine

# sessionmaker produces Session factories.
# declarative_base creates the ORM registry base class.
# Session is imported for the type hint in get_db().
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ---------------------------------------------------------------------------
# Connection URL
# ---------------------------------------------------------------------------
# Format: dialect://username:password@host:port/database
# In production this value should be read from an environment variable
# (e.g. os.getenv("DATABASE_URL")) so credentials are never hardcoded.
# It is hardcoded here for the current development phase as instructed.
DATABASE_URL = "postgresql://docmind:docmind123@localhost:5432/docmind"

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# create_engine() creates the connection pool — one engine per application.
# It does NOT open a connection immediately; the first query does that lazily.
#
# echo=False — suppresses SQL statement logging to stdout.
#              Set to True temporarily when debugging query issues.
engine = create_engine(DATABASE_URL, echo=False)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# sessionmaker() returns a factory class. Calling SessionLocal() produces
# a new Session instance — one per request in a FastAPI application.
#
# autocommit=False — transactions must be committed explicitly (db.commit()).
#                    This is the production-safe default; data is only written
#                    when you explicitly ask for it.
#
# autoflush=False  — pending ORM changes are not automatically sent to the
#                    database before queries. Gives full control over when
#                    writes happen, preventing surprise partial flushes.
#
# bind=engine      — links every session produced by this factory to the
#                    engine (and therefore the database) defined above.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------
# declarative_base() creates the ORM metadata registry. Every SQLAlchemy
# model (table definition) will subclass Base. The Base.metadata object
# knows about all registered models, enabling Base.metadata.create_all()
# to create all tables in one call.
# No tables are created by this line — it only creates the base class.
Base = declarative_base()


# ---------------------------------------------------------------------------
# FastAPI database dependency
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session for one request.

    Usage in a route:
        from app.database.database import get_db
        from sqlalchemy.orm import Session
        from fastapi import Depends

        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            db.query(...)

    Lifecycle:
        1. FastAPI calls get_db() before the route handler runs.
        2. A new Session is created and yielded to the handler.
        3. The handler uses db to query or write to the database.
        4. When the handler returns (or raises), the finally block closes
           the session and returns the connection to the pool.

    Yields:
        Session: An active SQLAlchemy session bound to the engine.
    """

    # Open a new session for this request.
    # SessionLocal() calls the factory and returns a fresh Session instance.
    db = SessionLocal()

    try:
        # Yield the session to the route handler.
        # FastAPI pauses here while the handler runs, injecting db as the
        # dependency value. Execution resumes here after the handler returns.
        yield db

    finally:
        # Always close the session — whether the handler succeeded, raised
        # an exception, or returned normally.
        # db.close() releases the connection back to the pool and discards
        # any uncommitted changes, preventing connection leaks.
        db.close()
