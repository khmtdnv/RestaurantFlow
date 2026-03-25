from application.dtos.cart import GetCartInputDTO
from domain.aggregates.cart import Cart
from domain.exceptions.cart import CartNotFoundError
from domain.interfaces.cart_repository import ICartRepository


class GetCartUseCase:
    """Получить текущее состояние корзины."""

    def __init__(self, cart_repo: ICartRepository):
        self.cart_repo = cart_repo

    async def execute(self, dto: GetCartInputDTO) -> Cart:
        cart = await self.cart_repo.get_by_user_id(dto.user_id)

        if not cart:
            raise CartNotFoundError(f"Корзина для пользователя с ID:{dto.user_id} не найдена.")

        return cart
