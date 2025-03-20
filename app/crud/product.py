from typing import List, Optional, Tuple, Dict, Any, Union

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.crud.base import CRUDBase
from app.db.models.product import Product
from app.schemas.product import ProductCreate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductCreate]):
    """CRUD operations for Product model."""
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Product]:
        """
        Get a product by name.
        
        Args:
            db: Database session
            name: Product name
            
        Returns:
            Product if found, None otherwise
        """
        return db.query(self.model).filter(self.model.name == name).first()
    
    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        """
        Get a product by SKU.
        
        Args:
            db: Database session
            sku: Product SKU
            
        Returns:
            Product if found, None otherwise
        """
        return db.query(self.model).filter(self.model.sku == sku).first()
    
    def create(self, db: Session, *, obj_in: ProductCreate) -> Product:
        """
        Create a new product with uniqueness validation.
        
        Args:
            db: Database session
            obj_in: Product data
            
        Returns:
            Created product
            
        Raises:
            HTTPException: If a product with the same name or SKU already exists
        """
        db_product = self.get_by_name(db, name=obj_in.name)
        if db_product:
            raise HTTPException(
                status_code=400,
                detail=f"Product with name '{obj_in.name}' already exists"
            )
        
        db_product = self.get_by_sku(db, sku=obj_in.sku)
        if db_product:
            raise HTTPException(
                status_code=400,
                detail=f"Product with SKU '{obj_in.sku}' already exists"
            )
        
        try:
            return super().create(db=db, obj_in=obj_in)
        except IntegrityError as e:
            db.rollback()
            if "uq_product_name" in str(e):
                raise HTTPException(
                    status_code=400, 
                    detail="A product with this name already exists"
                )
            elif "uq_product_sku" in str(e):
                raise HTTPException(
                    status_code=400, 
                    detail="A product with this SKU already exists"
                )
            raise HTTPException(
                status_code=400, 
                detail="Database integrity error occurred"
            )
    
    def update_stock(self, db: Session, *, product_id: int, quantity_change: int) -> Optional[Product]:
        """
        Update product stock. Use negative quantity_change to reduce stock.
        
        Args:
            db: Database session
            product_id: ID of the product to update
            quantity_change: Amount to change stock by (positive to add, negative to subtract)
            
        Returns:
            Product object if successful, None if product not found
        """
        product = self.get(db, id=product_id)
        if not product:
            return None
        
        product.stock += quantity_change
        
        if product.stock < 0:
            product.stock = 0
            
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def check_stock_availability(
        self, db: Session, product_id: int, quantity: int
    ) -> Tuple[bool, Optional[Product]]:
        """
        Check if a product has sufficient stock available.
        
        Args:
            db: Database session
            product_id: ID of the product to check
            quantity: Quantity required
            
        Returns:
            Tuple of (has_sufficient_stock, product)
        """
        product = self.get(db, id=product_id)
        if not product:
            return False, None
        return product.stock >= quantity, product


# Create a singleton instance
product = CRUDProduct(Product) 