from dataclasses import dataclass


@dataclass
class Transaction:
    order_id: str
    amount: str
    status: str
    payment_url: str | None = None
    external_payment_id: str | None = None
