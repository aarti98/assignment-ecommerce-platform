from typing import Tuple, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.crud.product import product as product_crud
from app.db.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate, OrderProductDetail
from app.schemas.product import Product as ProductSchema


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    """CRUD operations for Order model."""
    
    def create_with_stock_validation(self, db: Session, *, obj_in: OrderCreate) -> Tuple[Order, str]:
        """
        Create a new order with stock validation.
        
        Args:
            db: Database session
            obj_in: Order data
            
        Returns:
            Tuple of (Order object, message)
            
        Raises:
            HTTPException: If product does not exist or insufficient stock
        """
        # validate all products have sufficient stock
        total_price = 0.0
        insufficient_stock_items = []
        products_data = []  # Store product data for later use
        
        for item in obj_in.products:
            has_stock, product = product_crud.check_stock_availability(
                db, product_id=item.product_id, quantity=item.quantity
            )
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with ID {item.product_id} not found"
                )
            
            if not has_stock:
                insufficient_stock_items.append({
                    "product_id": item.product_id,
                    "available_stock": product.stock,
                    "requested_quantity": item.quantity
                })
            else:
                products_data.append((product, item.quantity))
                total_price += product.price * item.quantity
        
        if insufficient_stock_items:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Insufficient stock for some products",
                    "items": insufficient_stock_items
                }
            )
        
        db_order = Order(
            products=[{"product_id": item.product_id, "quantity": item.quantity} for item in obj_in.products],
            total_price=round(total_price, 2),
            status="pending"
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        for item in obj_in.products:
            product_crud.update_stock(db, product_id=item.product_id, quantity_change=-item.quantity)
        
        db_order.status = "completed"
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Store product data in a separate attribute for the API to use
        # We won't change the Order model but will make this data available
        db_order.product_details = products_data
            
        return db_order, "Order placed successfully"

    def get_order_with_product_details(self, db: Session, *, order_id: int) -> Optional[Order]:
        """
        Get order with full product details.
        
        Args:
            db: Database session
            order_id: ID of the order to retrieve
            
        Returns:
            Order with product details or None if not found
        """
        db_order = self.get(db, id=order_id)
        if not db_order:
            return None
            
        products_data = []
        for item in db_order.get_products():
            product = product_crud.get(db, id=item["product_id"])
            if product:
                products_data.append((product, item["quantity"]))
                
        db_order.product_details = products_data
        
        return db_order

    def process_order(self, db: Session, *, order_id: int) -> Tuple[Order, str]:
        """
        Process a pending order.
        
        Args:
            db: Database session
            order_id: ID of the order to process
            
        Returns:
            Tuple of (Order, message)
            
        Raises:
            HTTPException: If order not found
        """
        order = self.get(db, id=order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
        
        if order.status != "pending":
            return order, f"Order already {order.status}"
        
        order.status = "completed"
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order, "Order processed successfully"


# Create a singleton instance
order = CRUDOrder(Order) 