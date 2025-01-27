from datetime import datetime
from typing import ClassVar

from ..shared.base_schemas import CreateBase, InDBBase, ResponseBase, UpdateBase


# Properties to receive on item creation
class ItemCreate(CreateBase):
    test_data: str
    user_id: str


# Properties to receive on item update
class ItemUpdate(UpdateBase):
    test_data: str | None = None


# Properties to return to client
class Item(ResponseBase):
    test_data: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    table_name: ClassVar[str] = "items"


# Properties stored in DB
class ItemInDB(InDBBase):
    test_data: str
    user_id: str
    created_at: datetime
    updated_at: datetime
