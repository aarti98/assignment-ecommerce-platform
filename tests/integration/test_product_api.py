import pytest
from fastapi.testclient import TestClient


def test_read_products_empty(client: TestClient):
    response = client.get("/products/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product(client: TestClient):
    product_data = {
        "name": "Test Product",
        "sku": "TEST-001",
        "category": "Electronics",
        "description": "Test Description for a product",
        "price": 99.99,
        "stock": 10
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 201
    
    created_product = response.json()
    assert created_product["name"] == product_data["name"]
    assert created_product["sku"] == product_data["sku"]
    assert created_product["category"] == product_data["category"]
    assert created_product["description"] == product_data["description"]
    assert created_product["price"] == product_data["price"]
    assert created_product["stock"] == product_data["stock"]
    assert "id" in created_product


def test_create_product_duplicate_name(client: TestClient):
    product1_data = {
        "name": "Duplicate Name Product",
        "sku": "DUP-001",
        "category": "Electronics", 
        "description": "First product with this name",
        "price": 99.99,
        "stock": 10
    }
    
    client.post("/products/", json=product1_data)
    
    product2_data = {
        "name": "Duplicate Name Product", 
        "sku": "DUP-002",                
        "category": "Electronics", 
        "description": "Second product with same name",
        "price": 199.99,
        "stock": 20
    }
    
    response = client.post("/products/", json=product2_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_product_duplicate_sku(client: TestClient):
    product1_data = {
        "name": "First SKU Product",
        "sku": "SKU-TEST-001",
        "category": "Electronics", 
        "description": "First product with this SKU",
        "price": 99.99,
        "stock": 10
    }
    
    client.post("/products/", json=product1_data)
    
    product2_data = {
        "name": "Second SKU Product",     
        "sku": "SKU-TEST-001",        
        "category": "Electronics", 
        "description": "Second product with same SKU",
        "price": 199.99,
        "stock": 20
    }
    
    response = client.post("/products/", json=product2_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_read_products(client: TestClient):
    products = [
        {
            "name": "Product 1",
            "sku": "READ-001",
            "category": "Electronics",
            "description": "Description for product 1",
            "price": 99.99,
            "stock": 10
        },
        {
            "name": "Product 2",
            "sku": "READ-002",
            "category": "Home Goods",
            "description": "Description for product 2",
            "price": 199.99,
            "stock": 20
        }
    ]
    
    for product in products:
        client.post("/products/", json=product)
    
    response = client.get("/products/")
    assert response.status_code == 200
    
    response_data = response.json()
    assert len(response_data) >= len(products)
    
    product_names = [p["name"] for p in response_data]
    assert "Product 1" in product_names
    assert "Product 2" in product_names


def test_read_product(client: TestClient):
    product_data = {
        "name": "Test Product for Get",
        "sku": "GET-TEST-001",
        "category": "Clothing",
        "description": "Test Description for get",
        "price": 99.99,
        "stock": 10
    }
    
    response = client.post("/products/", json=product_data)
    created_product = response.json()
    
    response = client.get(f"/products/{created_product['id']}")
    assert response.status_code == 200
    
    product = response.json()
    assert product["id"] == created_product["id"]
    assert product["name"] == product_data["name"]
    assert product["sku"] == product_data["sku"]
    assert product["category"] == product_data["category"]
    assert product["description"] == product_data["description"]
    assert product["price"] == product_data["price"]
    assert product["stock"] == product_data["stock"]


def test_read_product_not_found(client: TestClient):
    response = client.get("/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_validation_product_create(client: TestClient):
    product_data = {
        "name": "Invalid Product",
        "sku": "INVALID-001",
        "category": "Test Category",
        "description": "Invalid Description",
        "price": -10.0,
        "stock": 10
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422
    
    product_data = {
        "name": "Invalid Product",
        "sku": "INVALID-001",
        "category": "Test Category",
        "description": "Invalid Description",
        "price": 99.99,
        "stock": -10
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422
    
    product_data = {
        "name": "Invalid Product",
        "sku": "INVALID@001",
        "category": "Test Category",
        "description": "Invalid Description",
        "price": 99.99,
        "stock": 10
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422