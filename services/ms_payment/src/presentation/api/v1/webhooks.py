import logging

from application.usecases.process_webhook import ProcessWebhookUseCase, WebhookDTO
from fastapi import APIRouter, Depends, Request, status
from presentation.dependencies import get_process_webhook_use_case

log = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/yookassa", status_code=status.HTTP_200_OK)
async def yookassa_webhook(
    request: Request, use_case: ProcessWebhookUseCase = Depends(get_process_webhook_use_case)
):
    try:
        payload = await request.json()
    except Exception:
        log.error("Получен некорректный JSON в вебхуке")
        return {"status": "error"}

    event = payload.get("event")
    payment_object = payload.get("object", {})
    payment_id = payment_object.get("id")

    metadata = payment_object.get("metadata", {})
    order_id = metadata.get("order_id")

    if not event or not payment_id:
        log.warning("Пропущен вебхук с неполными данными")
        return {"status": "ok"}

    dto = WebhookDTO(event=event, payment_id=payment_id, order_id=order_id)

    await use_case.execute(dto)

    return {"status": "ok"}
