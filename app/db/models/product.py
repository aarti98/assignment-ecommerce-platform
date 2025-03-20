from sqlalchemy import Column, Integer, String, Float, Text, UniqueConstraint

from app.db.base_class import Base


class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, unique=True)
    sku = Column(String(50), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    
    __table_args__ = (
        UniqueConstraint('name', name='uq_product_name'),
        UniqueConstraint('sku', name='uq_product_sku'),
    )
    
    def __repr__(self):
        return f"<Product {self.name}>" 