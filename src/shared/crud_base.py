from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

from supabase._async.client import AsyncClient

from ..supabase.schemas import UserIn
from .base_schemas import CreateBase, ResponseBase, UpdateBase

T = TypeVar("T", bound=ResponseBase)
CreateT = TypeVar("CreateT", bound=CreateBase)
UpdateT = TypeVar("UpdateT", bound=UpdateBase)

class IRepository(ABC, Generic[T, CreateT, UpdateT]):
    @abstractmethod
    async def get(self, db: AsyncClient, id: str) -> T | None:
        pass
    
    @abstractmethod
    async def get_all(self, db: AsyncClient) -> Sequence[T]:
        pass

    @abstractmethod
    async def create(self, db: AsyncClient, obj_in: CreateT) -> T:
        pass

    @abstractmethod
    async def update(self, db: AsyncClient, obj_in: UpdateT) -> T:
        pass

    @abstractmethod
    async def delete(self, db: AsyncClient, id: str) -> T:
        pass

class CRUDBase(IRepository[T, CreateT, UpdateT]):
    def __init__(self, model: type[T]):
        self.model = model

    async def get(self, db: AsyncClient, id: str) -> T | None:
        """get by table_name by id"""
        response = await db.table(self.model.table_name).select("*").eq("id", id).execute()
        return self.model(**response.data[0]) if response.data else None

    async def get_all(self, db: AsyncClient) -> Sequence[T]:
        """get all by table_name"""
        response = await db.table(self.model.table_name).select("*").execute()
        return [self.model(**item) for item in response.data]

    async def get_multi_by_owner(
        self, db: AsyncClient, user: UserIn
    ) -> Sequence[T]:
        """get by owner,use it if rls failed to use"""
        response = (
            await db.table(self.model.table_name)
            .select("*")
            .eq("user_id", user.id)
            .execute()
        )
        return [self.model(**item) for item in response.data]

    async def create(self, db: AsyncClient, obj_in: CreateT) -> T:
        """create by CreateSchemaType"""
        response = (
            await db.table(self.model.table_name).insert(obj_in.model_dump()).execute()
        )
        return self.model(**response.data[0])

    async def update(self, db: AsyncClient, obj_in: UpdateT) -> T:
        """update by UpdateSchemaType"""
        response = (
            await db.table(self.model.table_name)
            .update(obj_in.model_dump(exclude={"id"}))
            .eq("id", obj_in.id)
            .execute()
        )
        return self.model(**response.data[0])

    async def delete(self, db: AsyncClient, id: str) -> T:
        """remove by UpdateSchemaType"""
        response = (
            await db.table(self.model.table_name).delete().eq("id", id).execute()
        )
        return self.model(**response.data[0])
