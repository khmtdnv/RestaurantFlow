from application.dtos.cart import AddItemToCartInputDTO, GetCartInputDTO
from application.use_cases.cart.add_item import AddItemToCartUseCase
from application.use_cases.cart.get_cart import GetCartUseCase
from fastapi import APIRouter, Depends, status
from infrastructure.slowapi.rate_limit import limiter
from presentation.api.dtos.cart import AddItemToCartRequestDTO, CartResponseDTO
from presentation.dependencies import (
    add_item_to_cart_use_case,
    get_cart_use_case,
    get_current_user,
)

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


# 1. Получить текущую корзину (При открытии приложения).
# - Метод: GET /cart
# - Тело запроса от фронта: отсутствует
# - Что делает: Идет в Redis и получает текущее состояние корзины.
# - Ожидаемый ответ бэкенда:
# HTTP_200_OK
# JSON
# {
#     "total_price": "1250.00",
#     "items": [
#         {"dish_id": 1, "quantity": 2, "price": "500.00"},
#         {"dish_id": 3, "quantity": 1, "price": "250.00"},
#     ],
# }


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Посмотреть корзину.",
)
@limiter.limit("90/minute")
async def get_cart(
    user_id: int = Depends(get_current_user),
    use_case: GetCartUseCase = Depends(get_cart_use_case),
) -> CartResponseDTO:
    input_dto = GetCartInputDTO(user_id=user_id)
    cart = await use_case.execute(input_dto)
    response_dto = CartResponseDTO.model_validate(cart)
    return response_dto


# 2. Добавить блюдо (Кнопка "В корзину" или "+").
# - Метод: POST /cart/items
# - Тело запроса от фронта:
# JSON
# {
#   "dish_id": 1,
#   "quantity": 1
# }
# - Сценарий использования: Идет в БД таблицу menu_items ->
# -> получает объект MenuItem по айди блюда чтобы узнать его цену ->
# -> вызывает метод add_item агрегата с собранными данными.
# - Ожидаемый ответ бэкенда:
# JSON
# {
#     "total_price": "1250.00",
#     "items": [
#         {"dish_id": 1, "quantity": 2, "price": "500.00"},
#         {"dish_id": 3, "quantity": 1, "price": "250.00"},
#     ],
# }
@limiter.limit("30/minute")
@router.post(
    "/items",
    response_model=CartResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить позицию в корзину.",
)
async def add_item_to_cart(
    request_dto: AddItemToCartRequestDTO,
    user_id: int = Depends(get_current_user),
    use_case: AddItemToCartUseCase = Depends(add_item_to_cart_use_case),
) -> CartResponseDTO:
    input_dto = AddItemToCartInputDTO(
        user_id=user_id, dish_id=request_dto.dish_id, quantity=request_dto.quantity
    )
    cart = await use_case.execute(input_dto)
    response_dto = CartResponseDTO.model_validate(cart)

    return response_dto


# 3. Изменить количество (Кнопки "+" и "-" внутри корзины).
# - Метод: PATCH /cart/items/{dish_id}
# - Тело запроса от фронта:
# JSON
# {"quantity": 3}
# - Сценарий использования: Идет в Redis и ищет нужную корзину по user_id ->
# -> изменяет количество блюда на quantity по dish_id ->
# -> сохраняет новое состояние корзины
# - Ожидаемый ответ бэкенда:
# JSON
# {
#     "total_price": "1250.00",
#     "items": [
#         {"dish_id": 1, "quantity": 2, "price": "500.00"},
#         {"dish_id": 3, "quantity": 1, "price": "250.00"},
#     ],
# }

# 4. Убрать блюдо из корзины.
# - Метод: DELETE /cart/items/{dish_id}
# - Тело запроса от фронта: отсутствует
# - Сценарий использования: Идет в Redis и ищет нужную корзину по user_id ->
# -> убирает блюдо с указанным dish_id из корзины ->
# -> сохраняет новое состояние корзины
# - Ожидаемый ответ бэкенда:
# JSON
# {
#     "total_price": "1250.00",
#     "items": [
#         {"dish_id": 1, "quantity": 2, "price": "500.00"},
#         {"dish_id": 3, "quantity": 1, "price": "250.00"},
#     ],
# }

# 5. Очистить корзину полностью.
# - Метод: DELETE /cart
# - Тело запроса от фронта: отсутствует
# - Сценарий использования: Идет в Redis и удаляет содержимое хранилища по ключу
# - Ожидаемый ответ бэкенда: отсутствует
