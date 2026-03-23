from application.dtos.cart import AddItemToCartRequestDTO
from application.use_cases.cart.add_item import AddItemToCartUseCase
from fastapi import APIRouter, Depends, Response, status
from presentation.dependencies import get_add_item_to_cart_use_case, get_current_user_id

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить позицию в корзину",
    description="Добавляет блюдо в корзину пользователя. Если корзины нет — создает её.",
)
async def add_item_to_cart(
    request: AddItemToCartRequestDTO,
    user_id: int = Depends(get_current_user_id),
    use_case: AddItemToCartUseCase = Depends(get_add_item_to_cart_use_case),
):
    await use_case.execute(user_id=user_id, request=request)
    return Response(status_code=status.HTTP_201_CREATED)
