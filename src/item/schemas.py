from typing import ClassVar

from pydantic import ConfigDict

from ..shared.base_schemas import CreateBase, InDBBase, ResponseBase, UpdateBase


# Properties to receive on item creation
class ItemCreate(CreateBase):
    title: str
    description: str | None = None
    user_id: str | None = None  # Will be set by the API
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "My Item",
                "description": "This is my item description"
            }
        }
    )


# Properties to receive on item update
class ItemUpdate(UpdateBase):
    title: str | None = None
    description: str | None = None
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "item_id",
                "title": "Updated Item",
                "description": "Updated description"
            }
        }
    )


# Properties to return to client
class Item(ResponseBase):
    title: str
    description: str | None = None
    user_id: str
    created_at: str
    updated_at: str

    table_name: ClassVar[str] = "items"
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "item_id",
                "title": "My Item",
                "description": "Item description",
                "user_id": "user_id",
                "created_at": "2025-01-27T19:20:08Z",
                "updated_at": "2025-01-27T19:20:08Z"
            }
        }
    )


# Properties stored in DB
class ItemInDB(InDBBase):
    title: str
    description: str | None = None
    user_id: str
    created_at: str
    updated_at: str
