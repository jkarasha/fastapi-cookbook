from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from db import get_session
from models import Role
from security import decode_access_token, oauth2_scheme

router = APIRouter()

class UserCreateRequestWithRole(BaseModel):
    username: str
    email: EmailStr
    role: Role = Role.basic

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], 
                    session: Session = Depends(get_session)) -> UserCreateRequestWithRole:
    user = decode_access_token(token=token, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized!",
        )
    return UserCreateRequestWithRole(
        username=user.username, email=user.email, role=user.role
    )

def get_premium_user(current_user: Annotated[get_current_user, Depends()]):
    if current_user.role != Role.premium:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized!",
        )
    return current_user

@router.get("/welcome/all-users",responses={})
def all_users_can_access(user: Annotated[get_current_user, Depends()]):
    return f"Welcome {user.username}, welcome to your space!"

@router.get("/welcome/premium-users",responses={})
def only_premium_users_can_access(user: Annotated[get_current_user, Depends(get_premium_user)]):
    return f"Welcome {user.username}, welcome to your premium space!"