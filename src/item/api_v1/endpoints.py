from fastapi import APIRouter, Depends, HTTPException, status
from supabase._async.client import AsyncClient
import logging

from ...supabase.deps import get_db, get_current_user
from ...supabase.schemas import UserIn
from ..schemas import Item, ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=Item)
async def create_item(
    *,
    db: AsyncClient = Depends(get_db),
    current_user: UserIn = Depends(get_current_user),
    item_in: ItemCreate
) -> Item:
    """
    Create a new item.
    """
    try:
        # Set the user_id from the authenticated user
        data = item_in.model_dump()
        data["user_id"] = current_user.id
        
        logging.info(f"Creating item with data: {data}")
        response = await db.table("items").insert(data).execute()
        logging.info(f"Got response: {response}")
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create item"
            )
            
        return Item(**response.data[0])
    except Exception as e:
        logging.error(f"Error creating item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=list[Item])
async def read_items(
    *,
    db: AsyncClient = Depends(get_db),
    current_user: UserIn = Depends(get_current_user)
) -> list[Item]:
    """
    Retrieve all items for the current user.
    """
    try:
        response = await db.table("items").select("*").eq("user_id", current_user.id).execute()
        return [Item(**item) for item in response.data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{item_id}", response_model=Item)
async def read_item(
    *,
    db: AsyncClient = Depends(get_db),
    current_user: UserIn = Depends(get_current_user),
    item_id: str
) -> Item:
    """
    Get a specific item by ID.
    """
    try:
        response = await db.table("items").select("*").eq("id", item_id).eq("user_id", current_user.id).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
            
        return Item(**response.data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{item_id}", response_model=Item)
async def update_item(
    *,
    db: AsyncClient = Depends(get_db),
    current_user: UserIn = Depends(get_current_user),
    item_id: str,
    item_in: ItemUpdate
) -> Item:
    """
    Update an item.
    """
    try:
        # Verify item belongs to user
        existing = await db.table("items").select("*").eq("id", item_id).eq("user_id", current_user.id).single().execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        response = await db.table("items").update(item_in.model_dump()).eq("id", item_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not update item"
            )
            
        return Item(**response.data[0])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{item_id}", response_model=Item)
async def delete_item(
    *,
    db: AsyncClient = Depends(get_db),
    current_user: UserIn = Depends(get_current_user),
    item_id: str
) -> Item:
    """
    Delete an item.
    """
    try:
        # Verify item belongs to user
        existing = await db.table("items").select("*").eq("id", item_id).eq("user_id", current_user.id).single().execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        response = await db.table("items").delete().eq("id", item_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not delete item"
            )
            
        return Item(**response.data[0])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
