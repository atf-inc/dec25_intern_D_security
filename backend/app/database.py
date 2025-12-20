"""
Database configuration for ATF Sentinel
Supports both Cloud SQL (production) and local PostgreSQL (development)
Author: ANIRUDH S J
"""
import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

# SQLAlchemy Base for model definitions
Base = declarative_base()

# Global engine and session factory
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """
    Get database URL based on environment.
    
    For Cloud SQL: Uses Cloud SQL Python Connector
    For Local: Uses standard PostgreSQL connection string
    """
    # Check if running in Cloud Run with Cloud SQL
    instance_connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
    
    if instance_connection_name:
        # Cloud SQL connection using Unix socket
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASS", "")
        db_name = os.getenv("DB_NAME", "atf_sentinel")
        
        # Cloud Run provides Unix socket at /cloudsql/<instance>
        socket_path = f"/cloudsql/{instance_connection_name}"
        
        return f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock={socket_path}/.s.PGSQL.5432"
    
    # Local development - standard PostgreSQL URL
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/atf_sentinel"
    )


def init_engine():
    """
    Initialize the SQLAlchemy engine.
    Called once at application startup.
    """
    global _engine, _SessionLocal
    
    if _engine is not None:
        return _engine
    
    database_url = get_database_url()
    
    # Mask password for logging
    safe_url = database_url
    if "@" in database_url:
        parts = database_url.split("@")
        if ":" in parts[0]:
            safe_url = parts[0].rsplit(":", 1)[0] + ":***@" + parts[1]
    
    logger.info(f"🔌 Connecting to database: {safe_url}")
    
    try:
        # Cloud SQL Python Connector for production
        instance_connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")
        
        if instance_connection_name:
            from google.cloud.sql.connector import Connector
            
            connector = Connector()
            
            def get_conn():
                return connector.connect(
                    instance_connection_name,
                    "pg8000",
                    user=os.getenv("DB_USER", "postgres"),
                    password=os.getenv("DB_PASS", ""),
                    db=os.getenv("DB_NAME", "atf_sentinel"),
                )
            
            _engine = create_engine(
                "postgresql+pg8000://",
                creator=get_conn,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=2,
                pool_timeout=30,
                pool_recycle=1800,
            )
            logger.info("✅ Connected to Cloud SQL via Connector")
        else:
            # Local PostgreSQL
            _engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=2,
                pool_timeout=30,
                pool_recycle=1800,
                echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            )
            logger.info("✅ Connected to local PostgreSQL")
        
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )
        
        return _engine
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise


def get_engine():
    """Get the SQLAlchemy engine, initializing if needed."""
    if _engine is None:
        init_engine()
    return _engine


def get_session_local():
    """Get the session factory."""
    if _SessionLocal is None:
        init_engine()
    return _SessionLocal


@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    
    Usage:
        with get_db_session() as session:
            session.query(Model).all()
    """
    SessionLocal = get_session_local()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """
    Dependency for FastAPI endpoints.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in models."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created")


def drop_tables():
    """Drop all tables (use with caution!)."""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️ Database tables dropped")


# Health check function
def check_database_health() -> dict:
    """
    Check database connectivity.
    
    Returns:
        dict with status and details
    """
    from sqlalchemy import text
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

