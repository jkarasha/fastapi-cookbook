import os
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2     
from sqlalchemy.orm import Session

from db import get_session
from models import User
from operations import get_user

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = (
    "http://localhost:8000/github/auth/token"
)
GITHUB_AUTHORIZATION_URL = (
    "https://github.com/login/oauth/authorize"
)

def resolve_github_token(access_token: str = Depends(OAuth2()),
                         session: Session = Depends(get_session)) -> User | None:
    user_response = httpx.get(
        "https://api.github.com/user",
        headers={"Authorization": f"{access_token}"},
    ).json()
    username = user_response.get("login", "")
    user = get_user(session=session, username_or_email=username)
    if not user:
        email = user_response.get("email", "")
        user = get_user(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token is not valid!",
        )
    return user