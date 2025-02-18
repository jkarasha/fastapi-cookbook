from typing import Tuple, Annotated
from fastapi import HTTPException, Query, Depends, Path
from datetime import date, timedelta

def check_end_start_condition(start_date: date = Query(None), end_date: date = Query(None)):
    if end_date and end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be later than start_date")

def time_range(
    start: date | None = Query(
        default=date.today(),
        description="If not provided, the current date will be used.",
        examples=[date.today()]
    ),
    end: date | None = Query(
        default=None,
        examples=[date.today() + timedelta(days=7)]
    )
    ) -> Tuple[date, date | None]:
    check_end_start_condition(start_date=start, end_date=end)
    return start, end

def select_category(
    category: Annotated[
        str,
        Path(
            description="Kind of travel you are interested in",
            enum=[
                "cruises",
                "city-breaks",
                "resort-stays",
            ],
        ),
    ],
    ) -> str:
    return category

def check_coupon_validity(
    category: Annotated[select_category, Depends()],
    code: str | None = Query(
        None, description="Coupon code"
    ),
    ) -> bool:
    coupon_dict = {
        "cruises": "CRUISE10",
        "city-breaks": "CITYBREAK15",
        "resort-stays": "RESORT20",
    }
    if (
        code is not None
        and coupon_dict.get(category, ...) == code
    ):
        return True
    return False