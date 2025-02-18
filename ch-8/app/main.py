import logging
from typing import Annotated
from app.dependencies import time_range, select_category, check_coupon_validity
from fastapi import Depends, FastAPI, BackgroundTasks

from app.background_task import store_query_to_external_db

logger = logging.getLogger("uvicorn.error")

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
        return f"{message} {end}"
    return message

@app.get("/v2/trips/{category}")
def get_trips_by_category(
    background_tasks: BackgroundTasks,
    category: Annotated[select_category, Depends()],
    discount_applicable: Annotated[
        bool, Depends(check_coupon_validity)
    ],
):
    category = category.replace("-", " ").title()
    message = f"You requested {category} trips."

    if discount_applicable:
        message += (
            "\n. The coupon code is valid! "
            "You will get a discount!"
        )

    background_tasks.add_task(
        store_query_to_external_db, message
    )
    logger.info(
        "Query sent to background task, end of request."
    )
    return message