from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import ping_mongo_db_server

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ping_mongo_db_server()
    yield

app = FastAPI(lifespan=lifespan)

