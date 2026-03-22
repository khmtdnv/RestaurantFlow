from application.dto.cart import AddItemToCartRequest
from domain.aggregates.cart import Cart, CartItem


class AddItemToCartUseCase:
    def __init__(self, uow):
        self.uow = uow

    # async def execute(self, request: AddItemToCartRequest):
    #     price = await self.uow.
    #     Cart.add_item(dish_id=request.dish_id, quantity=)
