import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.product import ProductCreate
from app.crud.product import product as product_crud


def test_create_product(db: Session):
    product_data = ProductCreate(
        name="Test Product",
        sku="TEST-001",
        category="Test Category",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    
    product = product_crud.create(db=db, obj_in=product_data)
    
    assert product.id is not None
    assert product.name == "Test Product"
    assert product.sku == "TEST-001"
    assert product.category == "Test Category"
    assert product.description == "Test Description"
    assert product.price == 99.99
    assert product.stock == 10


def test_create_product_duplicate_name(db: Session):
    product_data1 = ProductCreate(
        name="Duplicate Name Test",
        sku="DUP-001",
        category="Test Category",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    product_crud.create(db=db, obj_in=product_data1)
    
    product_data2 = ProductCreate(
        name="Duplicate Name Test",
        sku="DUP-002",
        category="Test Category",
        description="Test Description 2",
        price=199.99,
        stock=20,
    )
    
    with pytest.raises(HTTPException) as excinfo:
        product_crud.create(db=db, obj_in=product_data2)
    
    assert excinfo.value.status_code == 400
    assert "already exists" in excinfo.value.detail


def test_create_product_duplicate_sku(db: Session):
    product_data1 = ProductCreate(
        name="SKU Test 1",
        sku="SKU-001",
        category="Test Category",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    product_crud.create(db=db, obj_in=product_data1)
    
    product_data2 = ProductCreate(
        name="SKU Test 2",
        sku="SKU-001",
        category="Test Category",
        description="Test Description 2",
        price=199.99,
        stock=20,
    )
    
    with pytest.raises(HTTPException) as excinfo:
        product_crud.create(db=db, obj_in=product_data2)
    
    assert excinfo.value.status_code == 400
    assert "already exists" in excinfo.value.detail


def test_get_product(db: Session):
    product_data = ProductCreate(
        name="Test Product for Get",
        sku="GET-001",
        category="Test Category",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    created_product = product_crud.create(db=db, obj_in=product_data)
    
    product = product_crud.get(db=db, id=created_product.id)
    
    assert product is not None
    assert product.id == created_product.id
    assert product.name == "Test Product for Get"
    assert product.sku == "GET-001"


def test_get_product_not_found(db: Session):
    product = product_crud.get(db=db, id=999)
    
    assert product is None


def test_get_products(db: Session):
    product_data1 = ProductCreate(
        name="Test Product 1",
        sku="MULTI-001",
        category="Test Category",
        description="Test Description 1",
        price=99.99,
        stock=10,
    )
    product_data2 = ProductCreate(
        name="Test Product 2",
        sku="MULTI-002",
        category="Test Category",
        description="Test Description 2",
        price=199.99,
        stock=20,
    )
    
    product_crud.create(db=db, obj_in=product_data1)
    product_crud.create(db=db, obj_in=product_data2)
    
    products = product_crud.get_multi(db=db)
    
    assert len(products) >= 2


def test_update_stock(db: Session):
    product_data = ProductCreate(
        name="Test Product for Stock Update",
        sku="STOCK-001",
        category="Test Category",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    product = product_crud.create(db=db, obj_in=product_data)
    
    updated_product = product_crud.update_stock(db=db, product_id=product.id, quantity_change=5)
    assert updated_product.stock == 15
    
    updated_product = product_crud.update_stock(db=db, product_id=product.id, quantity_change=-3)
    assert updated_product.stock == 12
    
    updated_product = product_crud.update_stock(db=db, product_id=product.id, quantity_change=-20)
    assert updated_product.stock == 0


def test_check_stock_availability(db: Session):
    product_data = ProductCreate(
        name="Test Product for Stock Check",
        sku="STOCK-001",
        category="Test Category",
        description="Test Description",
        price=99.99,
        stock=10,
    )
    product = product_crud.create(db=db, obj_in=product_data)
    
    # Check when enough stock
    has_stock, found_product = product_crud.check_stock_availability(
        db=db, product_id=product.id, quantity=5
    )
    assert has_stock is True
    assert found_product.id == product.id
    
    # Check when exactly enough stock
    has_stock, found_product = product_crud.check_stock_availability(
        db=db, product_id=product.id, quantity=10
    )
    assert has_stock is True
    assert found_product.id == product.id
    
    # Check when not enough stock
    has_stock, found_product = product_crud.check_stock_availability(
        db=db, product_id=product.id, quantity=15
    )
    assert has_stock is False
    assert found_product.id == product.id
    
    # Check when product not found
    has_stock, found_product = product_crud.check_stock_availability(
        db=db, product_id=999, quantity=5
    )
    assert has_stock is False
    assert found_product is None 