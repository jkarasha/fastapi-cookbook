from fastapi import (
    FastAPI,
    Depends,
    Request,
    HTTPException,
    status
)
from sqlalchemy.orm import Session
from pydantic import BaseModel

from protoapp.db import Item, SessionLocal
from protoapp.logging import client_logger

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_logger.info(
        f"method: {request.method}, "
        f"call: {request.url.path}, "
        f"ip: {request.client.host}"
    )
    response = await call_next(request)
    return response


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ItemSchema(BaseModel):
    name: str
    color: str

@app.get("/home")
async def read_main():
    return {"message": "Hello from ch-5!"}

@app.post("/item", response_model=int, status_code=status.HTTP_201_CREATED)
async def add_item(item: ItemSchema, db: Session = Depends(get_db_session)):
    db_item = Item(name=item.name, color=item.color)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item.id

@app.get("/item/{item_id}", response_model=ItemSchema)
async def get_item(item_id: int, db: Session = Depends(get_db_session)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_item