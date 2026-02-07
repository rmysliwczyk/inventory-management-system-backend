import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import func, select

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
def read_asset_types(session: SessionDep) -> Sequence[AssetTypePublic]:
    asset_types = session.exec(select(AssetType)).all()
    asset_types_public = []
    for asset_type in asset_types:
        assets_count = len(asset_type.assets)
        asset_types_public.append(
            AssetTypePublic.model_validate(
                {
                    **asset_type.model_dump(),
                    "quantity": assets_count,
                    "assets": asset_type.assets,
                }
            )
        )

    return asset_types_public


@router.get(
    "/{asset_type_id}",
    response_model=AssetTypePublic,
    dependencies=[Depends(allowed_roles([UserRole.ADMIN, UserRole.USER]))],
)
def read_asset_type(asset_type_id: uuid.UUID, session: SessionDep) -> AssetTypePublic:
    asset_type = session.exec(
        select(AssetType).where(AssetType.id == asset_type_id)
    ).first()
    if asset_type is None:
        raise HTTPException(status_code=404, detail="Requested asset type not found.")

    asset_type = AssetTypePublic.model_validate(asset_type)

    asset_type.quantity = len(asset_type.assets)
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


@router.delete(
    "/{asset_type_id}",
    status_code=204,
    dependencies=[Depends(allowed_roles([UserRole.ADMIN]))],
)
def delete_asset_type(session: SessionDep, asset_type_id: uuid.UUID):
    asset_type = session.exec(
        select(AssetType).where(AssetType.id == asset_type_id)
    ).first()
    if asset_type is None:
        raise HTTPException(status_code=404, detail="Requested asset type not found.")
    session.delete(asset_type)
    session.commit()
