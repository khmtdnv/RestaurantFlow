from application.dto.cart import AddItemToCartRequest
from application.use_cases.add_item_to_cart import AddItemToCartUseCase
from fastapi import APIRouter, Depends, status

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
    responses={404: {"description": "Not found"}},
)


# @router.post(
#     "/items",
#     status_code=status.HTTP_201_CREATED,
#     summary="Добавить позицию в корзину",
#     description="Добавляет блюдо в корзину пользователя. Если корзины нет — создает её.",
# )
# async def add_item_to_cart(
#     payload: AddItemToCartRequest,
#     user_id: int = Depends(get_current_user_id),
# ):
#     use_case = AddItemToCartUseCase()
#     result = use_case.execute(user_id=user_id, item=payload)
#     return result
