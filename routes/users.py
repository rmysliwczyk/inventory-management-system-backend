from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..dependencies import SessionDep, allowed_roles, get_current_user, hash_password
from ..models.user import User, UserCreate, UserPublic, UserRole

router = APIRouter(tags=["Users"], prefix="/users")


@router.get(
    "/",
    response_model=list[UserPublic],
    dependencies=[Depends(allowed_roles([UserRole.ADMIN]))],
)
def read_users(session: SessionDep) -> Sequence[User]:
    response = session.exec(select(User)).all()
    return response


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.get(
    "/{id}",
    response_model=UserPublic,
    dependencies=[Depends(allowed_roles([UserRole.ADMIN]))],
)
def read_user(id: int, session: SessionDep) -> User:
    user_read = session.exec(select(User).where(User.id == id)).one()
    return user_read


@router.post(
    "/",
    response_model=UserPublic,
    dependencies=[Depends(allowed_roles([UserRole.ADMIN]))],
)
def create_user(
    new_user: UserCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> User:
    existing_user = session.exec(
        select(User).where(User.username == new_user.username)
    ).first()
    if existing_user is None:
        user_created = User(
            **new_user.model_dump(), hashed_password=hash_password(new_user.password)
        )
    else:
        raise HTTPException(
            status_code=409, detail="User with that username already exists."
        )
    session.add(user_created)
    session.commit()
    session.refresh(user_created)
    return user_created
