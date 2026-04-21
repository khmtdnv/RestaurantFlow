from dataclasses import dataclass

from domain.interfaces.payment_gateway import IPaymentGateway


@dataclass
class CreatePaymentDTO:
    order_id: str
    amount: str


class CreatePaymentUseCase:
    def __init__(self, gateway: IPaymentGateway):  # + repo
        self.gateway = gateway

    async def execute(self, dto: CreatePaymentDTO) -> str | None:
        transaction = await self.gateway.generate_payment_link(
            order_id=dto.order_id, amount=dto.amount
        )

        if not transaction:
            raise

        return transaction.payment_url
