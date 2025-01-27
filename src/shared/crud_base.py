from typing import Generic, TypeVar

from supabase._async.client import AsyncClient

from ..supabase.schemas import UserIn
from .base_schemas import CreateBase, ResponseBase, UpdateBase

ModelType = TypeVar("ModelType", bound=ResponseBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=CreateBase)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=UpdateBase)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncClient, *, id: str) -> ModelType | None:
        """get by table_name by id"""
        response = await db.table(self.model.table_name).select("*").eq("id", id).execute()
        return self.model(**response.data[0]) if response.data else None

    async def get_all(self, db: AsyncClient) -> list[ModelType]:
        """get all by table_name"""
        response = await db.table(self.model.table_name).select("*").execute()
        return [self.model(**item) for item in response.data]

    async def get_multi_by_owner(
        self, db: AsyncClient, *, user: UserIn
    ) -> list[ModelType]:
        """get by owner,use it  if rls failed to use"""
        response = (
            await db.table(self.model.table_name)
            .select("*")
            .eq("user_id", user.id)
            .execute()
        )
        return [self.model(**item) for item in response.data]

    async def create(self, db: AsyncClient, *, obj_in: CreateSchemaType) -> ModelType:
        """create by CreateSchemaType"""
        response = (
            await db.table(self.model.table_name).insert(obj_in.model_dump()).execute()
        )
        return self.model(**response.data[0])

    async def update(self, db: AsyncClient, *, obj_in: UpdateSchemaType) -> ModelType:
        """update by UpdateSchemaType"""
        response = (
            await db.table(self.model.table_name)
            .update(obj_in.model_dump(exclude={"id"}))
            .eq("id", obj_in.id)
            .execute()
        )
        return self.model(**response.data[0])

    async def delete(self, db: AsyncClient, *, id: str) -> ModelType:
        """remove by UpdateSchemaType"""
        response = (
            await db.table(self.model.table_name).delete().eq("id", id).execute()
        )
        return self.model(**response.data[0])
