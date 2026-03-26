from application.dtos.order import CreateOrderInputDTO
from application.use_cases.order.create_order import CreateOrderUseCase
from fastapi import APIRouter, Depends, status
from presentation.api.dtos.order import OrderResponseDTO
from presentation.dependencies import (
    create_order_use_case,
    get_current_user,
)

router = APIRouter(
    prefix="/order",
    tags=["Order"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ.",
)
async def create_order(
    user_id: int = Depends(get_current_user),
    use_case: CreateOrderUseCase = Depends(create_order_use_case),
) -> OrderResponseDTO:
    input_dto = CreateOrderInputDTO(user_id=user_id)
    order = await use_case.execute(input_dto)
    response_dto = OrderResponseDTO.model_validate(order)
    return response_dto
