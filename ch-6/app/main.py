from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db import Base
from app.db_connection import (
    AsyncSessionLocal,
    get_db_session,
    get_engine,
)
from app.operations import (
    create_ticket,
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