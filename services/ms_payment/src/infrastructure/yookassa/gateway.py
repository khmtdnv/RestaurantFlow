from domain.entities import Transaction
from domain.interfaces.payment_gateway import IPaymentGateway
from infrastructure.yookassa.client import YookassaClient
from infrastructure.yookassa.schemas import (
    Amount,
    Confirmation,
    PaymentCreateRequest,
    PaymentMethodData,
)


class YookassaGatewayAdapter(IPaymentGateway):
    def __init__(self, client: YookassaClient):
        self.client = client

    async def generate_payment_link(self, order_id: str, amount: str) -> Transaction | None:
        yoo_request = PaymentCreateRequest(
            amount=Amount(value=str(amount), currency="RUB"),
            payment_method_data=PaymentMethodData(type="bank_card"),
            confirmation=Confirmation(),
            capture=True,
            description=f"Оплата заказа {order_id}",
            metadata={"order_id": order_id},
        )

        yoo_response = await self.client.create_payment(yoo_request)

        url = None
        if yoo_response.confirmation:
            url = yoo_response.confirmation.confirmation_url

            return Transaction(
                order_id=order_id,
                amount=amount,
                status="pending",
                external_payment_id=yoo_response.id,
                payment_url=url,
            )
        else:
            return None
