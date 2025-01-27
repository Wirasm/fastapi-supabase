from fastapi import APIRouter, HTTPException

from ...supabase.deps import CurrentUser, SessionDep
from ..crud import item
from ..schemas import Item, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/create-item")
async def create_item(item_in: ItemCreate, session: SessionDep, user: CurrentUser) -> Item:
    # Set the user_id from the authenticated user
    item_in.user_id = user.id
    return await item.create(session, obj_in=item_in)


@router.get("/read-all-item")
async def read_items(session: SessionDep, user: CurrentUser) -> list[Item]:
    """Get all items for the current user"""
    return await item.get_multi_by_owner(session, user=user)


@router.get("/get-by-id/{id}")
async def read_item_by_id(id: str, session: SessionDep, user: CurrentUser) -> Item:
    """Get an item by ID, ensuring it belongs to the current user"""
    db_item = await item.get(session, id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_item


@router.get("/get-by-owner")
async def read_item_by_owner(session: SessionDep, user: CurrentUser) -> list[Item]:
    """Get all items owned by the current user"""
    return await item.get_multi_by_owner(session, user=user)


@router.put("/update-item/{id}")
async def update_item(
    id: str, item_in: ItemUpdate, session: SessionDep, user: CurrentUser
) -> Item:
    """Update an item, ensuring it belongs to the current user"""
    db_item = await item.get(session, id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await item.update(session, obj_in=item_in)


@router.delete("/delete/{id}")
async def delete_item(id: str, session: SessionDep, user: CurrentUser) -> Item:
    """Delete an item, ensuring it belongs to the current user"""
    db_item = await item.get(session, id=id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await item.delete(session, id=id)
