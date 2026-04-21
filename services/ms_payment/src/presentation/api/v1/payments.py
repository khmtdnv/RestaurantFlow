from application.usecases.create_payment import CreatePaymentDTO, CreatePaymentUseCase
from fastapi import APIRouter, Depends, HTTPException, status
from presentation.api.schemas.payments import OrderPaymentRequest, OrderPaymentResponse
from presentation.dependencies import get_create_payment_use_case

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=OrderPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: OrderPaymentRequest,
    use_case: CreatePaymentUseCase = Depends(get_create_payment_use_case),
):
    dto = CreatePaymentDTO(order_id=request.order_id, amount=request.amount)

    payment_url = await use_case.execute(dto)

    if not payment_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Не удалось сгенерировать ссылку на оплату",
        )

    return OrderPaymentResponse(payment_url=payment_url)
