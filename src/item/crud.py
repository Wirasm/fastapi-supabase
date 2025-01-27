from src.shared.crud_base import CRUDBase
from src.item.schemas import Item, ItemCreate, ItemUpdate

class ItemRepository(CRUDBase[Item, ItemCreate, ItemUpdate]):
    def __init__(self):
        super().__init__(Item)

item_repository = ItemRepository()
