import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..dependencies import SessionDep, allowed_roles
from ..models.asset import Asset, AssetCreate, AssetPublic
from ..models.user import UserRole

router = APIRouter(tags=["Assets"], prefix="/assets")


@router.get(
    "/",
    dependencies=[Depends(allowed_roles([UserRole.ADMIN, UserRole.USER]))],
    response_model=list[AssetPublic],
)
def read_assets(session: SessionDep) -> Sequence[Asset]:
    results = session.exec(select(Asset)).all()
    return results


@router.get(
    "/{asset_id}",
    dependencies=[Depends(allowed_roles([UserRole.ADMIN, UserRole.USER]))],
    response_model=AssetPublic,
)
def read_asset(session: SessionDep, asset_id: uuid.UUID) -> Asset:
    result = session.exec(select(Asset).where(Asset.id == asset_id)).first()
    if not result:
        raise HTTPException(
            status_code=404, detail="Couldn't find an asset with the provided id."
        )
    return result


@router.post(
    "/",
    dependencies=[Depends(allowed_roles([UserRole.ADMIN]))],
    response_model=AssetPublic,
)
def create_asset(new_asset: AssetCreate, session: SessionDep) -> Asset:
    created_asset = Asset.model_validate(new_asset)
    session.add(created_asset)
    session.commit()
    session.refresh(created_asset)
    return created_asset


@router.delete(
    "/{asset_id}",
    status_code=204,
    dependencies=[Depends(allowed_roles([UserRole.ADMIN]))],
)
def delete_asset(session: SessionDep, asset_id: uuid.UUID):
    asset = session.exec(select(Asset).where(Asset.id == asset_id)).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Requested asset not found.")
    session.delete(asset)
    session.commit()
