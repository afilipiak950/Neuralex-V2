"""
Database session management for async SQLAlchemy
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Convert postgresql:// to postgresql+asyncpg://
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif not DATABASE_URL:
    # Fallback for development
    DATABASE_URL = "postgresql+asyncpg://localhost:5432/neuralex"

# Engine configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=300,
    poolclass=NullPool if "sqlite" in DATABASE_URL else None,
    connect_args={
        "server_settings": {
            "application_name": "neuralex-platform",
        }
    } if "postgresql" in DATABASE_URL else {}
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    Usage:
        async with get_db() as db:
            # use db session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def get_db_session() -> AsyncSession:
    """
    Get a database session for dependency injection
    Usage with FastAPI:
        async def endpoint(db: AsyncSession = Depends(get_db_session)):
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def init_database():
    """
    Initialize database tables
    This should be called on application startup
    """
    try:
        from app.db.models import Base
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def drop_database():
    """
    Drop all database tables
    WARNING: This will delete all data!
    """
    try:
        from app.db.models import Base
        
        async with engine.begin() as conn:
            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
            
        logger.info("Database tables dropped successfully")
        
    except Exception as e:
        logger.error(f"Failed to drop database: {e}")
        raise

async def check_database_connection() -> bool:
    """
    Check if database connection is working
    Returns True if connection is successful, False otherwise
    """
    try:
        async with get_db() as db:
            # Execute a simple query
            result = await db.execute("SELECT 1")
            return result.scalar() == 1
            
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

async def get_database_info() -> dict:
    """
    Get database information and statistics
    """
    try:
        async with get_db() as db:
            # Get PostgreSQL version
            version_result = await db.execute("SELECT version()")
            version = version_result.scalar()
            
            # Get database size (PostgreSQL specific)
            size_result = await db.execute(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            )
            size = size_result.scalar()
            
            # Get table information
            tables_result = await db.execute("""
                SELECT schemaname, tablename, 
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            tables = tables_result.fetchall()
            
            return {
                "version": version,
                "database_size": size,
                "tables": [
                    {
                        "schema": table.schemaname,
                        "name": table.tablename,
                        "size": table.size
                    }
                    for table in tables
                ],
                "connection_url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
            }
            
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "error": str(e),
            "connection_url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
        }

# Connection pool monitoring
async def get_pool_status() -> dict:
    """Get connection pool status"""
    try:
        pool = engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
        }
    except Exception as e:
        logger.error(f"Failed to get pool status: {e}")
        return {"error": str(e)}

# Health check for database
async def database_health_check() -> dict:
    """
    Comprehensive database health check
    """
    health_data = {
        "status": "unknown",
        "connection": False,
        "latency": None,
        "pool": {},
        "info": {}
    }
    
    try:
        import time
        
        # Test connection and measure latency
        start_time = time.time()
        health_data["connection"] = await check_database_connection()
        health_data["latency"] = round((time.time() - start_time) * 1000, 2)  # ms
        
        if health_data["connection"]:
            health_data["status"] = "healthy"
            health_data["pool"] = await get_pool_status()
            health_data["info"] = await get_database_info()
        else:
            health_data["status"] = "unhealthy"
            
    except Exception as e:
        health_data["status"] = "error"
        health_data["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_data
