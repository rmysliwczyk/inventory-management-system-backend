import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .asset import Asset


class AssetTypeBase(SQLModel):
    name: str = Field(max_length=128)
    description: str | None = Field(default=None, max_length=2048)


class AssetType(AssetTypeBase, table=True):
    __tablename__ = "AssetType"  # type: ignore
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    assets: list["Asset"] = Relationship(
        back_populates="asset_type", cascade_delete=True
    )


class AssetTypePublic(AssetTypeBase):
    id: uuid.UUID
    assets: list["Asset"]
    quantity: int = 0


class AssetTypeCreate(AssetTypeBase):
    pass


class AssetTypeUpdate(AssetTypeBase):
    pass
