import logging

from application.dtos.order import CreateOrderInputDTO, CreateOrderResultDTO
from domain.aggregates.order import Order, OrderItem
from domain.exceptions.cart import CartNotFoundError
from domain.exceptions.menu import MenuItemNotFoundError, MenuItemUnavailableError
from domain.interfaces.cart_repository import ICartRepository
from domain.interfaces.payment_client import IPaymentClient
from domain.interfaces.uow import IUnitOfWork

log = logging.getLogger(__name__)


class CreateOrderUseCase:
    """Формирование заказа из содержимого корзины пользователя."""

    def __init__(
        self,
        uow: IUnitOfWork,
        cart_repo: ICartRepository,
        payment_client: IPaymentClient,
    ):
        self.uow = uow
        self.cart_repo = cart_repo
        self.payment_client = payment_client

    async def execute(self, dto: CreateOrderInputDTO):
        # 1. Получаем корзину и строго проверяем её наполненность
        cart = await self.cart_repo.get_by_user_id(dto.user_id)
        if not cart or not cart.items:
            raise CartNotFoundError(f"Корзина пользователя {dto.user_id} пуста или не найдена.")

        async with self.uow:
            # 2. Достаем все блюда ОДНИМ запросом
            dish_ids = {item.dish_id for item in cart.items}
            menu_items = await self.uow.menu_repo.get_by_ids(list(dish_ids))

            # Проверяем целостность данных (вдруг блюдо удалили из БД)
            if len(dish_ids) != len(menu_items):
                raise MenuItemNotFoundError("Некоторые блюда из корзины больше не доступны в меню.")

            # Собираем словарь актуальных цен для быстрого доступа
            actual_prices = {}
            for mi in menu_items:
                if not mi.is_available:
                    raise MenuItemUnavailableError(f"Блюдо с ID:{mi.id} сейчас недоступно")
                actual_prices[mi.id] = mi.price
            # 3. Трансформируем элементы
            order_items = [
                OrderItem(
                    dish_id=item.dish_id,
                    quantity=item.quantity,
                    price=actual_prices[item.dish_id],  # Берем цену из БД
                )
                for item in cart.items
            ]

            # 4. Формируем доменный Агрегат
            order = Order(user_id=cart.user_id)
            order.add_items(order_items)

            # 5. Сохраняем в БД и фиксируем транзакцию
            order_id = await self.uow.order_repo.create(order)
            await self.uow.commit()

        # 6. Обновляем доменную модель и чистим Redis
        order.set_id(order_id)
        await self.cart_repo.delete(cart.user_id)

        payment_url = None
        try:
            payment_url = await self.payment_client.create_payment(
                order_id=order_id,
                amount=order.total_price,
            )
        except Exception as e:
            log.error(f"Не удалось получить ссылку на оплату для заказа {order.id}: {e}")

        return {
            "status": order.status,
            "items": order.items,
            "total_price": order.total_price,
            "payment_url": payment_url,
        }
