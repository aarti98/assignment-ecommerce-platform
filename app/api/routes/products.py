from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.product import product as crud_product
from app.db.session import get_db
from app.schemas.product import Product, ProductCreate

router = APIRouter()


@router.get("/", response_model=List[Product])
def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Retrieve all products.
    
    Parameters:
    - skip: Number of products to skip (pagination)
    - limit: Maximum number of products to return
    
    Returns:
    - List of products
    """
    products = crud_product.get_multi(db, skip=skip, limit=limit)
    return products


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new product.
    
    Parameters:
    - product: Product data including name, SKU, category, description, price, and stock
    
    Returns:
    - Created product
    
    Raises:
    - 400: If a product with the same name or SKU already exists
    - 422: If validation fails (invalid format for fields)
    """
    try:
        return crud_product.create(db=db, obj_in=product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{product_id}", response_model=Product)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific product by ID.
    
    Parameters:
    - product_id: ID of the product to retrieve
    
    Returns:
    - Product with matching ID
    
    Raises:
    - 404: If product not found
    """
    db_product = crud_product.get(db, id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )
    return db_product 