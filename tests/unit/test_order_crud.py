import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.product import ProductCreate
from app.schemas.order import OrderCreate, OrderProductItem
from app.crud.product import product as product_crud
from app.crud.order import order as order_crud


def test_create_order_with_stock_validation(db: Session):
    product_data = ProductCreate(
        name="Test Product for Order",
        sku="ORDER-TEST-001",
        category="Electronics",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    product = product_crud.create(db=db, obj_in=product_data)
    
    order_data = OrderCreate(
        products=[
            OrderProductItem(product_id=product.id, quantity=2)
        ]
    )
    
    db_order, message = order_crud.create_with_stock_validation(db=db, obj_in=order_data)
    
    assert db_order.id is not None
    assert hasattr(db_order, 'product_details')
    assert len(db_order.product_details) == 1
    product_detail = db_order.product_details[0]
    assert product_detail[1] == 2
    assert product_detail[0].id == product.id
    assert product_detail[0].name == product.name
    assert product_detail[0].sku == product.sku
    assert product_detail[0].category == product.category
    assert db_order.total_price == product.price * 2
    assert db_order.status == "completed"
    assert message == "Order placed successfully"
    
    updated_product = product_crud.get(db=db, id=product.id)
    assert updated_product.stock == 8 


def test_create_order_product_not_found(db: Session):
    order_data = OrderCreate(
        products=[
            OrderProductItem(product_id=999, quantity=2)
        ]
    )
    
    with pytest.raises(HTTPException) as excinfo:
        order_crud.create_with_stock_validation(db=db, obj_in=order_data)
    
    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail


def test_create_order_insufficient_stock(db: Session):
    product_data = ProductCreate(
        name="Limited Stock Product",
        sku="LIMITED-TEST-001",
        category="Electronics",
        description="Product with limited stock",
        price=99.99,
        stock=3,
    )
    product = product_crud.create(db=db, obj_in=product_data)
    
    order_data = OrderCreate(
        products=[
            OrderProductItem(product_id=product.id, quantity=5)
        ]
    )
    
    with pytest.raises(HTTPException) as excinfo:
        order_crud.create_with_stock_validation(db=db, obj_in=order_data)
    
    assert excinfo.value.status_code == 400
    assert "Insufficient stock" in excinfo.value.detail["message"]
    
    updated_product = product_crud.get(db=db, id=product.id)
    assert updated_product.stock == 3


def test_get_order_with_product_details(db: Session):
    product_data = ProductCreate(
        name="Test Product for Order Get",
        sku="ORDER-GET-TEST-001",
        category="Books",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    product = product_crud.create(db=db, obj_in=product_data)
    

    order_data = OrderCreate(
        products=[
            OrderProductItem(product_id=product.id, quantity=2)
        ]
    )
    
    created_order, _ = order_crud.create_with_stock_validation(db=db, obj_in=order_data)
    
    order_details = order_crud.get_order_with_product_details(db=db, order_id=created_order.id)
    
    assert order_details is not None
    assert order_details.id == created_order.id
    assert hasattr(order_details, 'product_details')
    assert len(order_details.product_details) == 1
    product_detail = order_details.product_details[0]
    assert product_detail[1] == 2  
    assert product_detail[0].id == product.id
    assert product_detail[0].name == product.name
    assert product_detail[0].sku == product.sku
    assert product_detail[0].category == product.category
    assert product_detail[0].price == product.price


def test_get_order_with_product_details_not_found(db: Session):
    order_details = order_crud.get_order_with_product_details(db=db, order_id=999)
    
    assert order_details is None


def test_create_order_with_multiple_products(db: Session):
    product_data1 = ProductCreate(
        name="Multi-Order Product 1",
        sku="MULTI-ORDER-001",
        category="Electronics",
        description="First product for multi-product order",
        price=99.99,
        stock=10,
    )
    product_data2 = ProductCreate(
        name="Multi-Order Product 2",
        sku="MULTI-ORDER-002",
        category="Clothing",
        description="Second product for multi-product order",
        price=49.99,
        stock=20,
    )
    
    product1 = product_crud.create(db=db, obj_in=product_data1)
    product2 = product_crud.create(db=db, obj_in=product_data2)
    
    order_data = OrderCreate(
        products=[
            OrderProductItem(product_id=product1.id, quantity=2),
            OrderProductItem(product_id=product2.id, quantity=3)
        ]
    )
    
    db_order, message = order_crud.create_with_stock_validation(db=db, obj_in=order_data)
    
    assert db_order.id is not None
    assert hasattr(db_order, 'product_details')
    assert len(db_order.product_details) == 2
    
    expected_total = (product1.price * 2) + (product2.price * 3)
    assert db_order.total_price == expected_total
    
    updated_product1 = product_crud.get(db=db, id=product1.id)
    assert updated_product1.stock == 8 
    
    updated_product2 = product_crud.get(db=db, id=product2.id)
    assert updated_product2.stock == 17


def test_get_order(db: Session):
    product_data = ProductCreate(
        name="Test Product for Order Get",
        sku="ORDER-GET-TEST-001",
        category="Test Category",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    product = product_crud.create(db=db, obj_in=product_data)
    
    order_data = OrderCreate(
        products=[
            OrderProductItem(product_id=product.id, quantity=2)
        ]
    )
    db_order, _ = order_crud.create_with_stock_validation(db=db, obj_in=order_data)
    
    order = order_crud.get(db=db, id=db_order.id)
    
    assert order is not None
    assert order.id == db_order.id
    assert order.total_price == db_order.total_price
    assert order.status == db_order.status


def test_get_order_not_found(db: Session):
    order = order_crud.get(db=db, id=999)
    
    assert order is None


def test_process_order_not_found(db: Session):
    with pytest.raises(HTTPException) as excinfo:
        order_crud.process_order(db=db, order_id=999)
    
    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.detail


