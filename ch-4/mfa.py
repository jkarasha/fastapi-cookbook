import pyotp
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from db import get_session
from operations import get_user
from rbac import get_current_user
from schemas import UserCreateResponse

router = APIRouter()

def generate_totp_secret():
    return pyotp.random_base32()


def generate_totp_uri(secret, user_email):
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email, issuer_name="YourAppName"
    )

@router.post("/user/enable-mfa")
def enable_mfa(
    user: UserCreateResponse = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    secret = generate_totp_secret()
    user = get_user(session=session, username_or_email=user.username)
    user.totp_secret = secret
    session.add(user)
    session.commit()
    totp_uri = generate_totp_uri(secret, user.username)

    return {"totp_uri": totp_uri, "secret-numbers": secret}

@router.post("/verify-totp")
def verify_totp(
    code: str,
    username: str,
    session: Session = Depends(get_session),
):
    user = get_user(session=session, username_or_email=username)
    if not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is not valid!",
        )
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not valid!",
        )
    return {"message": "Token verified successfully!"}