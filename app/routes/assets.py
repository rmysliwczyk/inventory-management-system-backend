from typing import Sequence

from fastapi import APIRouter, Depends
from sqlmodel import select

from ..dependencies import SessionDep, allowed_roles
from ..models.asset import Asset, AssetCreate
from ..models.user import UserRole

router = APIRouter(tags=["Assets"], prefix="/assets")


@router.get("/", dependencies=[Depends(allowed_roles([UserRole.ADMIN, UserRole.USER]))])
def read_assets(session: SessionDep) -> Sequence[Asset]:
    results = session.exec(select(Asset)).all()
    return results


@router.post("/", dependencies=[Depends(allowed_roles([UserRole.ADMIN]))])
def create_asset(new_asset: AssetCreate, session: SessionDep) -> Asset:
    created_asset = Asset.model_validate(new_asset)
    session.add(created_asset)
    session.commit()
    session.refresh(created_asset)
    return created_asset
