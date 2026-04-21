from unittest.mock import AsyncMock

import pytest
from fastapi import status
from presentation.dependencies import add_item_to_cart_use_case, get_current_user


# Класс-заглушка для имитации данных из БД/Redis
class FakeCart:
    def __init__(self):
        self.total_price = 1000.00
        self.items = [{"dish_id": 5, "quantity": 2, "price": 500.00}]


@pytest.mark.asyncio
async def test_add_item_to_cart(client):  # client берется из conftest.py
    # --- ARRANGE ---
    payload = {"dish_id": 5, "quantity": 2}

    # Мокаем UseCase
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = FakeCart()

    # Подменяем зависимости в твоем приложении
    from main import app

    app.dependency_overrides[get_current_user] = lambda: 1
    app.dependency_overrides[add_item_to_cart_use_case] = lambda: mock_use_case

    # --- ACT ---
    response = await client.post("/api/v1/cart/items", json=payload)

    # --- ASSERT ---
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["total_price"] == "1000.00"
    assert data["items"][0]["dish_id"] == 5
    assert data["items"][0]["quantity"] == 2
