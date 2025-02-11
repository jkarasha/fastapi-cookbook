from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    TicketRequest, TicketUpdateRequest, TicketDetailsUpateRequest,
    TicketResponse
)

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        # create database and tables based on the current metadata
        #await conn.run_sync(Base.metadata.create_all)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket

@app.put("/ticket/{ticket_id}")
async def update_ticket_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    ticket_id: int,
    ticket_update: TicketUpdateRequest
    ):
    
    update_dict_args = ticket_update.model_dump(exclude_unset=True)

    updated = await update_ticket(
        db_session, ticket_id, update_dict_args
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    
    return {"detail": "Ticket updated successfully"}

@app.put("/ticket/{ticket_id}/price/{new_price}")
async def update_ticket_price_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    ticket_id: int,
    new_price: float
    ):
    
    updated = await update_ticket_price(
        db_session, ticket_id, new_price
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    
    return {"detail": "Ticket price updated successfully"}

@app.delete("/ticket/{ticket_id}")
async def delete_ticket_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    ticket_id: int
    ):
    
    deleted_ticket = await delete_ticket(db_session, ticket_id)
    if not deleted_ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    
    return {"detail": "Ticket deleted successfully"}


@app.get("/tickets/{show}", response_model=list[TicketResponse])
async def get_tickets_for_show_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    show: str
    ):
    
    tickets = await get_all_tickets_for_show(db_session, show)

    return [TicketResponse(id=t.id) for t in tickets]


@app.post("/event", response_model=dict[str, int])
async def create_event_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    event_name: str,
    nb_tickets: int | None = 0,
    ):
    
    event_id = await create_event(db_session, event_name, nb_tickets)

    return {"event_id": event_id}


#register sponsor to event
@app.post("/sponsor/{sponsor_name}")
async def register_sponsor_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    sponsor_name: str,
    ):
    
    sponsor_id = await create_sponsor(db_session, sponsor_name)
    if not sponsor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sponsor not created")
    
    return {"sponsor_id": sponsor_id}


@app.post("/event/{event_id}/sponsor/{sponsor_id}")
async def register_sponsor_amount_contribution(
    db_session: Annotated[
        AsyncSession, Depends(get_db_session)
    ],
    sponsor_id: int,
    event_id: int,
    amount: float | None = 0,
):
    registered = await add_sponsor_to_event(
        db_session, event_id, sponsor_id, amount
    )
    if not registered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contribution not registered",
        )

    return {"detail": "Contribution registered"}