from fastapi import APIRouter, Depends, HTTPException, status
from supabase._async.client import AsyncClient
import logging

from src.supabase.deps import get_db, get_current_user
from src.supabase.schemas import UserIn
from src.item.schemas import Item, ItemCreate, ItemUpdate
from src.item.crud import item_repository

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
        item = await item_repository.create(db, obj_in=ItemCreate(**data))
        logging.info(f"Created item: {item}")
        return item
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
        items = await item_repository.get_multi_by_owner(db, user=current_user)
        return list(items)
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
        item = await item_repository.get(db, id=item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
            
        if item.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
            
        return item
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
        item = await item_repository.get(db, id=item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        if item.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Set the ID in the update object
        update_data = item_in.model_dump()
        update_data["id"] = item_id
        update_obj = ItemUpdate(**update_data)
        
        return await item_repository.update(db, obj_in=update_obj)
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
        item = await item_repository.get(db, id=item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
            
        if item.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return await item_repository.delete(db, id=item_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
