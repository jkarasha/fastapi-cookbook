from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base
from app.db_connection import (
    AsyncSessionLocal,
    get_db_session,
    get_engine,
)
from app.operations import (
    create_ticket,
    delete_ticket,
    get_ticket,
    update_ticket_price,
)

class TicketRequest(BaseModel):
    price: float | None
    user: str | None = None
    show: str | None


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.post("/ticket", response_model=dict[str, int])
async def create_ticket_route(
    ticket: TicketRequest,
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ]):
    ticket_id = await create_ticket(db_session, ticket.show, ticket.user, ticket.price)
    return {"ticket_id": ticket_id}

@app.get("/ticket/{ticket_id}")
async def get_ticket_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    ticket_id: int
):
    ticket = await get_ticket(db_session, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket