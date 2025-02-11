from pydantic import BaseModel, Field

class TicketRequest(BaseModel):
    price: float | None
    user: str | None = None
    show: str | None

class TicketDetailsUpateRequest(BaseModel):
    seat: str | None = None
    ticket_type: str | None = None


class TicketUpdateRequest(BaseModel):
    price: float | None = Field(None, ge=0)

class TicketResponse(TicketRequest):
    id: int