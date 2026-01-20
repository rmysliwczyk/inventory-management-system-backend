import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlmodel import Session, select

from .cryptography import hash_password
from .initialize_database import get_engine
from .models.asset import Asset
from .models.asset_type import AssetType
from .models.user import User, UserRole

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE = os.environ["ACCESS_TOKEN_EXPIRE"]


def get_session():
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Included token is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") == None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    current_user = session.exec(
        select(User).where(User.username == payload["sub"])
    ).first()
    if current_user is None:
        raise credentials_exception
    else:
        return current_user


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(int(ACCESS_TOKEN_EXPIRE))
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str, session: SessionDep) -> bool | User:
    requested_user = session.exec(select(User).where(User.username == username)).first()
    if requested_user is None or requested_user.hashed_password != hash_password(
        password
    ):
        return False
    else:
        return requested_user


def allowed_roles(allowed_roles: list[UserRole]):
    authorization_exception = HTTPException(status_code=401, detail="Not authorized")

    def check_role(current_user: Annotated[User, Depends(get_current_user)]):
        if current_user.role not in allowed_roles:
            raise authorization_exception

    return check_role


def IntegrityErrorHandler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=400,
        content={"detail": "Related resource with provided ID was not found."},
    )
