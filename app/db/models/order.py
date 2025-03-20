import json
from datetime import datetime
from typing import Dict, List

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON

from app.db.base_class import Base


class Order(Base):
    id = Column(Integer, primary_key=True, index=True)
    products = Column(JSON, nullable=False, default=list)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Order {self.id}>"
    
    def get_products(self) -> List[Dict]:
        """Get the products list from the JSON column."""
        if isinstance(self.products, str):
            return json.loads(self.products)
        return self.products 