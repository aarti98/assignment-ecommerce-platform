from fastapi.testclient import TestClient


def create_test_products(client):
    products = [
        {
            "name": "Test Product 1",
            "sku": "ORDER-001",
            "category": "Electronics",
            "description": "Test Description 1",
            "price": 99.99,
            "stock": 10
        },
        {
            "name": "Test Product 2",
            "sku": "ORDER-002",
            "category": "Home Goods",
            "description": "Test Description 2",
            "price": 199.99,
            "stock": 5
        }
    ]
    
    created_products = []
    for product in products:
        response = client.post("/products/", json=product)
        created_products.append(response.json())
    
    return created_products


def test_place_order_success(client: TestClient):
    products = create_test_products(client)
    
    order_data = {
        "products": [
            {
                "product_id": products[0]["id"],
                "quantity": 2
            },
            {
                "product_id": products[1]["id"],
                "quantity": 1
            }
        ]
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    
    order = response.json()
    assert "id" in order
    assert "total_price" in order
    assert "status" in order
    assert "message" in order
    assert "products" in order
    
    assert len(order["products"]) == 2
    for product_item in order["products"]:
        assert "product" in product_item
        assert "quantity" in product_item
        assert "id" in product_item["product"]
        assert "name" in product_item["product"]
        assert "sku" in product_item["product"]
        assert "category" in product_item["product"]
        assert "description" in product_item["product"]
        assert "price" in product_item["product"]
        assert "stock" in product_item["product"]
    
    expected_price = (products[0]["price"] * 2) + (products[1]["price"] * 1)
    assert order["total_price"] == expected_price
    
    assert order["status"] == "completed"
    
    response = client.get(f"/products/{products[0]['id']}")
    assert response.json()["stock"] == 8 
    
    response = client.get(f"/products/{products[1]['id']}")
    assert response.json()["stock"] == 4  

def test_place_order_product_not_found(client: TestClient):
    order_data = {
        "products": [
            {
                "product_id": 999,
                "quantity": 2
            }
        ]
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_place_order_insufficient_stock(client: TestClient):
    product_data = {
        "name": "Limited Stock Product",
        "sku": "LIMITED-001",
        "category": "Electronics",
        "description": "Product with limited stock",
        "price": 99.99,
        "stock": 3
    }
    
    response = client.post("/products/", json=product_data)
    product = response.json()
    
    order_data = {
        "products": [
            {
                "product_id": product["id"],
                "quantity": 5 
            }
        ]
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]["message"]
    
    response = client.get(f"/products/{product['id']}")
    assert response.json()["stock"] == 3


def test_get_order_by_id(client: TestClient):
    product_data = {
        "name": "Test Product for Order",
        "sku": "ORDER-GET-001",
        "category": "Books",
        "description": "Test Description",
        "price": 99.99,
        "stock": 10
    }
    
    response = client.post("/products/", json=product_data)
    product = response.json()
    
    order_data = {
        "products": [
            {
                "product_id": product["id"],
                "quantity": 2
            }
        ]
    }
    
    response = client.post("/orders/", json=order_data)
    created_order = response.json()
    
    response = client.get(f"/orders/{created_order['id']}")
    assert response.status_code == 200
    
    order = response.json()
    assert order["id"] == created_order["id"]
    assert len(order["products"]) == 1
    assert order["products"][0]["quantity"] == 2
    assert order["products"][0]["product"]["id"] == product["id"]
    assert order["products"][0]["product"]["name"] == product["name"]
    assert order["products"][0]["product"]["sku"] == product["sku"]
    assert order["products"][0]["product"]["category"] == product["category"]


def test_get_order_not_found(client: TestClient):
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_validation_order_create(client: TestClient):
    order_data = {
        "products": [
            {
                "product_id": 1,
                "quantity": -1 
            }
        ]
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 422 