from application.dtos.cart import AddItemToCartInputDTO
from domain.aggregates.cart import Cart
from domain.exceptions.menu import MenuItemNotFoundError, MenuItemUnavailableError
from domain.interfaces.cart_repository import ICartRepository
from domain.interfaces.menu_repository import IMenuItemRepository


class AddItemToCartUseCase:
    """Добавлению блюда в корзину."""

    def __init__(
        self,
        cart_repo: ICartRepository,
        menu_repo: IMenuItemRepository,
    ):
        self.cart_repo = cart_repo
        self.menu_repo = menu_repo

    async def execute(self, dto: AddItemToCartInputDTO) -> Cart:
        menu_item = await self.menu_repo.get_by_id(dto.dish_id)

        if not menu_item:
            raise MenuItemNotFoundError(f"Блюдо с ID:{dto.dish_id} не найдено.")

        if not menu_item.is_available:
            raise MenuItemUnavailableError(f"Блюдо с ID:{dto.dish_id} сейчас не в наличии.")

        cart = await self.cart_repo.get_or_create_by_user_id(dto.user_id)

        cart.add_item(dish_id=dto.dish_id, quantity=dto.quantity, price=menu_item.price)
        await self.cart_repo.save(cart)

        return cart
