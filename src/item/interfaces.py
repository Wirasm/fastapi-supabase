from abc import ABC, abstractmethod
from supabase._async.client import AsyncClient
from src.item.schemas import Item, ItemCreate, ItemUpdate

class IItemRepository(ABC):
    @abstractmethod
    async def get(self, db: AsyncClient, id: str) -> Item | None:
        pass

    @abstractmethod 
    async def get_all(self, db: AsyncClient) -> list[Item]:
        pass

    @abstractmethod
    async def create(self, db: AsyncClient, obj_in: ItemCreate) -> Item:
        pass

    @abstractmethod
    async def update(self, db: AsyncClient, obj_in: ItemUpdate) -> Item:
        pass

    @abstractmethod
    async def delete(self, db: AsyncClient, id: str) -> Item:
        pass
