from application.dto.order import AddItemRequest, OrderOut
from application.use_cases.add_item import AddItemToOrderUseCase
from fastapi import APIRouter, status
from presentation.api.dependencies import UOWDependency

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/{order_id}/items", response_model=OrderOut, status_code=status.HTTP_201_CREATED
)
async def add_item(
    order_id: int,
    request: AddItemRequest,
    uow: UOWDependency,
):
    use_case = AddItemToOrderUseCase(uow=uow)
    result = await use_case.execute(order_id=order_id, request=request)

    return result
