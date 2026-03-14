from application.dto.orders import OrderCreateIn, OrderOut
from application.use_cases.create_order import CreateOrderUseCase
from fastapi import APIRouter, status
from presentation.api.dependencies import UOWDependency

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def add_order(
    request_data: OrderCreateIn,
    uow: UOWDependency,
):
    use_case = CreateOrderUseCase(uow)
    result = await use_case.execute(request_data)

    return result
