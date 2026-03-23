from application.dtos.cart import AddItemToCartRequestDTO
from domain.exceptions.menu import MenuItemNotFoundError, MenuItemUnavailableError
from domain.interfaces.repositories import ICartRepository, IMenuItemRepository


class AddItemToCartUseCase:
    """Use case: adding new position to cart."""

    def __init__(
        self,
        cart_repo: ICartRepository,
        menu_repo: IMenuItemRepository,
    ):
        self.cart_repo = cart_repo
        self.menu_repo = menu_repo

    async def execute(self, user_id: int, request: AddItemToCartRequestDTO) -> None:
        menu_item = await self.menu_repo.get_by_id(request.dish_id)

        if not menu_item:
            raise MenuItemNotFoundError(f"Dish:{request.dish_id} were not found.")

        if not menu_item.is_available:
            raise MenuItemUnavailableError(f"Dish:{request.dish_id} currently not available.")

        cart = await self.cart_repo.get_by_user_id(user_id)

        cart.add_item(dish_id=request.dish_id, quantity=request.quantity, price=menu_item.price)
        await self.cart_repo.save(cart)
