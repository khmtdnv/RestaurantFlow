import json
from decimal import Decimal

from domain.aggregates.cart import Cart, CartItem
from domain.interfaces.cart_repository import ICartRepository
from redis.asyncio import Redis


class RedisCartRepository(ICartRepository):
    """
    Cart storage redis implementation.
    Redis key sample: 'cart:user:123'.
    """

    # cart automatically gonna be removed after 7 days
    CART_TTL_SECONDS = 60 * 60 * 24 * 7

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _get_key(self, user_id: int) -> str:
        """Creates redis key string by user_id."""
        return f"cart:user:{user_id}"

    def _serialize_cart(self, cart: Cart) -> dict:
        """Aggregate -> Dictionary"""
        return {
            "user_id": cart.user_id,
            "items": [
                {
                    "dish_id": item.dish_id,
                    "quantity": item.quantity,
                    "price": str(item.price),
                }
                for item in cart.items
            ],
        }

    def _deserialize_cart(self, data: dict) -> Cart:
        """Dictionary -> Aggregate"""
        user_id = data.get("user_id", [])
        items = [
            CartItem(
                dish_id=item["dish_id"],
                quantity=item["quantity"],
                price=Decimal(item["price"]),
            )
            for item in data.get("items", [])
        ]
        return Cart(user_id=user_id, items=items)

    async def get_by_user_id(self, user_id: int) -> Cart:
        raw_data = await self.redis.get(self._get_key(user_id))

        # if there is no existing cart for user create him a new one
        if not raw_data:
            return Cart(user_id=user_id)

        data = json.loads(raw_data)

        return self._deserialize_cart(data)

    async def save(self, cart: Cart) -> None:
        cart_dict = self._serialize_cart(cart)
        await self.redis.set(
            name=self._get_key(cart.user_id),
            value=json.dumps(cart_dict),
            ex=self.CART_TTL_SECONDS,
        )

    async def delete(self, user_id: int) -> None:
        await self.redis.delete(self._get_key(user_id))
