
import pytest
from unittest.mock import patch, Mock
import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    # Reset inventory to a known state before each test so tests
    # don't affect each other.
    app_module.inventory = [
        {"id": 1, "barcode": 20304567, "name": "Almond milk", "price": 250, "quantity": 67, "brand": "brookside"},
        {"id": 2, "barcode": 20304667, "name": "bread", "price": 450, "quantity": 89, "brand": "Super Loaf"}
    ]
    app_module.next_id = 3
    with app_module.app.test_client() as client:
        yield client


def test_get_all_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


def test_get_single_item_found(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Almond milk"


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_add_item(client):
    new_item = {
        "barcode": 11111,
        "name": "Eggs",
        "brand": "Kenchic",
        "price": 300,
        "quantity": 20
    }
    response = client.post("/inventory", json=new_item)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Eggs"
    assert data["id"] == 3

    # Confirm it actually got added to the list
    get_response = client.get("/inventory")
    assert len(get_response.get_json()) == 3


def test_add_item_missing_field(client):
    response = client.post("/inventory", json={"name": "Incomplete"})
    assert response.status_code == 400


def test_update_item(client):
    response = client.patch("/inventory/1", json={"price": 275})
    assert response.status_code == 200
    assert response.get_json()["price"] == 275


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"price": 100})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 200

    get_response = client.get("/inventory")
    assert len(get_response.get_json()) == 1


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404




@patch("app.requests.get")
def test_lookup_external_product_found(mock_get, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar"
        }
    }
    mock_get.return_value = mock_response

    response = client.get("/external/123456")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Organic Almond Milk"


@patch("app.requests.get")
def test_lookup_external_product_not_found(mock_get, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": 0}
    mock_get.return_value = mock_response

    response = client.get("/external/000000")
    assert response.status_code == 404