from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.order import order as crud_order
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponseWithDetails, OrderProductDetail
from app.schemas.product import Product as ProductSchema

router = APIRouter()


@router.post("/", response_model=OrderResponseWithDetails)
def place_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
):
    """
    Place a new order.
    
    This endpoint will:
    1. Validate that all products exist and have sufficient stock
    2. Create the order with "pending" status
    3. Reduce the stock of each product
    4. Update the order status to "completed"
    
    Parameters:
    - order: Order data containing products and quantities
    
    Returns:
    - Order details with product information and confirmation message
    
    Raises:
    - 404: If any product in the order doesn't exist
    - 400: If any product has insufficient stock
    """
    try:
        db_order, message = crud_order.create_with_stock_validation(db=db, obj_in=order)
        
        # Transform Order object to OrderResponseWithDetails
        products_with_details = []
        for product, quantity in db_order.product_details:
            products_with_details.append(
                OrderProductDetail(
                    product=ProductSchema.model_validate(product),
                    quantity=quantity
                )
            )
            
        result = OrderResponseWithDetails(
            id=db_order.id,
            products=products_with_details,
            total_price=db_order.total_price,
            status=db_order.status,
            created_at=db_order.created_at,
            message=message
        )
        
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error placing order: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your order."
        )


@router.get("/{order_id}", response_model=OrderResponseWithDetails)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
):
    """
    Get order details by ID with complete product information.
    
    Parameters:
    - order_id: ID of the order to retrieve
    
    Returns:
    - Order details with product information
    
    Raises:
    - 404: If order not found
    """
    db_order = crud_order.get_order_with_product_details(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    products_with_details = []
    for product, quantity in db_order.product_details:
        products_with_details.append(
            OrderProductDetail(
                product=ProductSchema.model_validate(product),
                quantity=quantity
            )
        )
        
    result = OrderResponseWithDetails(
        id=db_order.id,
        products=products_with_details,
        total_price=db_order.total_price,
        status=db_order.status,
        created_at=db_order.created_at,
        message="Order details retrieved successfully"
    )
    
    return result 