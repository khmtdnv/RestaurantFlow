from pydantic import BaseModel


class OrderPaymentRequest(BaseModel):
    order_id: str
    amount: str


class OrderPaymentResponse(BaseModel):
    payment_url: str
