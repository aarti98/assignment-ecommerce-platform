from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.product import Product as ProductSchema


class OrderProductItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than zero')
        return v


class OrderProductDetail(BaseModel):
    """Order product item with full product details."""
    product: ProductSchema
    quantity: int


class OrderBase(BaseModel):
    products: List[OrderProductItem]


class OrderCreate(OrderBase):
    pass


class OrderUpdate(OrderBase):
    products: Optional[List[OrderProductItem]] = None
    status: Optional[str] = None


class OrderInDB(OrderBase):
    id: int
    total_price: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Order(OrderInDB):
    pass


class OrderResponseWithDetails(BaseModel):
    """Additional response model for order creation with product details."""
    id: int
    products: List[OrderProductDetail]
    total_price: float
    status: str
    created_at: datetime
    message: str = "Order placed successfully"


class OrderResponse(BaseModel):
    """Response model for order creation."""
    id: int
    total_price: float
    status: str
    message: str = "Order placed successfully"


class InsufficientStockError(BaseModel):
    """Error response for insufficient stock."""
    detail: str
    product_id: int
    available_stock: int
    requested_quantity: int 