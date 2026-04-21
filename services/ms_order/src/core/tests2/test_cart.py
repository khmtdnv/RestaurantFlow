from unittest.mock import AsyncMock

import pytest
from fastapi import status
from presentation.dependencies import get_current_user


class FakeCart:
    def __init__(self):
        self.total_price = 1000.00
        self.items = [{"dish_id": 5, "quantity": 2, "price": 500.00}]


@pytest.mark.asyncio
async def test_get_cart_success(client, clean_redis):
    from main import app

    test_user_id = 1
    app.dependency_overrides[get_current_user] = lambda: {"id": test_user_id, "is_superuser": False}
    cart_key = f"cart:{test_user_id}"
    await clean_redis.set(
        cart_key,
        '{"total_price": 1000.00, "items": [{"dish_id": 5, "quantity": 2, "price": 500.0}]}',
    )
    response = await client.get("/api/v1/cart")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total_price"] == 1000.0
