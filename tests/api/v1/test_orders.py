from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.core.auth import get_current_user
from shared_models import Order, User
from unittest.mock import MagicMock

client = TestClient(app)

# Mock the database dependency
db_session = MagicMock(spec=Session)

def override_get_db():
    try:
        yield db_session
    finally:
        pass

# Mock the authentication dependency
def override_get_current_user():
    return User(id="test_user", roles=["manager"])


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_create_order():
    order_data = {
        "farmer_id": "farmer1",
        "merchant_id": "merchant1",
        "product_id": "product1",
        "quantity": 10,
        "unit_price": 5.0,
    }
    response = client.post("/api/v1/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert "order" in data
    assert "escrow" in data
    assert data["order"]["quantity"] == 10
