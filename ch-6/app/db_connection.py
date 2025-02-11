from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

# DB Name, should pull from a configuration file
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./database.db"

# Using DB URL, connect to a 
def get_engine():
    return create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True,
    )

# used to encapsulate a session, each request will get its own session
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=get_engine(), class_=AsyncSession
)

async def get_db_session():
    #using async with creates a scoped call. Session closed and connection closed when the scope ends
    async with AsyncSessionLocal() as session:
        yield session