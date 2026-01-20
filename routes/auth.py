from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import select

from ..cryptography import verify_hashed_password
from ..dependencies import SessionDep, create_access_token
from ..models.user import User

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> dict:
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if verify_hashed_password(form_data.password, user.hashed_password) == False:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
