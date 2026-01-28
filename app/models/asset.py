import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .asset_type import AssetType


class AssetBase(SQLModel):
    description: str | None = Field(
        description="Additional description for the asset.", max_length=2056
    )


class Asset(AssetBase, table=True):
    __tablename__ = "Asset"  # type: ignore
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    asset_type_id: uuid.UUID = Field(foreign_key="AssetType.id")
    asset_type: "AssetType" = Relationship(back_populates="assets")


class AssetCreate(AssetBase):
    asset_type_id: uuid.UUID

class AssetPublic(AssetBase):
    id: uuid.UUID
    description: str | None
