from typing import Annotated
from app.dependencies import time_range
from fastapi import Depends, FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/v1/trips")
def get_trips(
    time_range: Annotated[time_range, Depends()]
    ):
    start, end = time_range
    message = f"Request trips from {start} to {end}"
    if end:
        return f"{message} {end})"
    return message