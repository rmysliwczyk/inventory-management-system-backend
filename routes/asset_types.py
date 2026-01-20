import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..dependencies import SessionDep, allowed_roles
from ..models.asset import Asset
from ..models.asset_type import AssetType, AssetTypeCreate, AssetTypePublic
from ..models.user import UserRole

router = APIRouter(tags=["Asset types"], prefix="/asset-types")

AssetTypePublic.model_rebuild()


@router.get(
    "/",
    response_model=list[AssetTypePublic],
    dependencies=[Depends(allowed_roles([UserRole.ADMIN, UserRole.USER]))],
)
def read_asset_types(session: SessionDep) -> Sequence[AssetType]:
    asset_types = session.exec(select(AssetType)).all()
    return asset_types


@router.get(
    "/{asset_type_id}",
    response_model=AssetTypePublic,
    dependencies=[Depends(allowed_roles([UserRole.ADMIN, UserRole.USER]))],
)
def read_asset_type(asset_type_id: uuid.UUID, session: SessionDep) -> AssetType:
    asset_type = session.exec(
        select(AssetType).where(AssetType.id == asset_type_id)
    ).first()
    if asset_type is None:
        raise HTTPException(status_code=404, detail="Requested asset type not found.")
    return asset_type


@router.post(
    "/",
    response_model=AssetTypePublic,
    dependencies=[Depends(allowed_roles([UserRole.ADMIN, UserRole.USER]))],
)
def create_asset_type(
    new_asset_type: AssetTypeCreate, session: SessionDep
) -> AssetType:
    created_asset_type = AssetType.model_validate(new_asset_type)
    session.add(created_asset_type)
    session.commit()
    session.refresh(created_asset_type)
    return created_asset_type
