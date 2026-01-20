import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .asset import Asset


class AssetTypeBase(SQLModel):
    name: str = Field(default="Asset type name", max_length=128)


class AssetType(AssetTypeBase, table=True):
    __tablename__ = "AssetType"  # type: ignore
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    assets: list["Asset"] = Relationship(back_populates="asset_type")
    quantity: int = Field(default=0)


class AssetTypePublic(AssetTypeBase):
    id: uuid.UUID
    assets: list["Asset"]


class AssetTypeCreate(AssetTypeBase):
    pass
