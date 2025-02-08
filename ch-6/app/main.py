from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db import Base
from app.db_connection import (
    AsyncSessionLocal,
    get_db_session,
    get_engine,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
