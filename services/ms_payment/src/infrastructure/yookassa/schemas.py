from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict


class PaymentServiceException(BaseModel):
    type: str
    id: str
    code: str
    description: str
    parameter: str | None = None


class Amount(BaseModel):
    value: str  # Сумма в выбранной валюте (дробное значение)
    currency: str  # Код валюты в формате ISO-4217


class Recipient(BaseModel):
    account_id: str  # Идентификатор магазина в ЮKassa
    gateway_id: str  # Идентификатор субаккаунта


class CardProduct(BaseModel):
    code: str  # Код карточного продукта (напр. MCP)
    name: str | None = None  # Название продукта (напр. MIR Privilege)


class CardResponse(BaseModel):
    last4: str
    expiry_year: str
    expiry_month: str
    card_type: str  # MasterCard, Visa, Mir и т.д.
    first6: str | None = None
    card_product: CardProduct | None = None
    issuer_country: str | None = None
    issuer_name: str | None = None
    source: str | None = None


class PaymentMethod(BaseModel):
    type: str  # bank_card и др.
    id: str
    saved: bool
    status: str  # pending, active, inactive
    title: str | None = None
    card: CardResponse | None = None


class Confirmation(BaseModel):
    type: str = "redirect"
    confirmation_url: str | None = None
    enforce: bool | None = None
    return_url: str = "https://www.example.com/return_url"


class CancellationDetails(BaseModel):
    party: str  # yoo_money, payment_network, merchant
    reason: str  # Причина отмены


class ThreeDSecure(BaseModel):
    applied: bool  # Была ли попытка аутентификации через 3-D Secure
    protocol: str | None = None  # Версия протокола: "v1" или "v2"
    # Иногда приходят дополнительные технические поля, лучше разрешить лишнее
    model_config = {"extra": "ignore"}


class AuthorizationDetails(BaseModel):
    three_d_secure: ThreeDSecure  # Объект с данными о 3DS
    rrn: str | None = None
    auth_code: str | None = None


class Settlement(BaseModel):
    type: str  # payout
    amount: Amount


class Deal(BaseModel):
    id: str
    settlements: List[Settlement]


class Transfer(BaseModel):
    account_id: str
    amount: Amount
    status: str  # pending, succeeded и т.д.
    platform_fee_amount: Amount | None = None
    description: str | None = None
    metadata: Dict[str, Any] | None = None


class Card(BaseModel):
    number: str
    expiry_year: str
    expiry_month: str
    cardholder: str | None = None
    csc: str | None = None


class PaymentMethodData(BaseModel):
    type: str
    card: Card | None = None


class Payment(BaseModel):
    # Обязательные поля (Required)
    id: str
    status: str  # pending, waiting_for_capture, succeeded, canceled
    amount: Amount
    recipient: Recipient
    created_at: str
    test: bool
    paid: bool
    refundable: bool

    # Необязательные поля (Optional)
    income_amount: Amount | None = None
    description: str | None = None
    payment_method: PaymentMethod | None = None
    captured_at: str | None = None
    expires_at: str | None = None
    confirmation: Confirmation | None = None
    refunded_amount: Amount | None = None
    receipt_registration: str | None = None  # pending, succeeded, canceled
    metadata: Dict[str, Any] | None = None
    cancellation_details: CancellationDetails | None = None
    authorization_details: AuthorizationDetails | None = None
    transfers: List[Transfer] | None = None
    deal: Deal | None = None
    merchant_customer_id: str | None = None

    model_config = ConfigDict(extra="ignore")


class PaymentList(BaseModel):
    type: str
    items: list[Payment]
    next_cursor: str | None = None

    model_config = ConfigDict(extra="ignore")


class PaymentCreateRequest(BaseModel):
    amount: Amount  # {"amount": {"value": "2.00", "currency": "RUB"}}"
    payment_method_data: PaymentMethodData
    confirmation: Confirmation
    capture: bool | None
    description: str | None  # "Оплата заказа № 72 для user@yoomoney.ru"
    metadata: dict[str, Any]


class PaymentConfirmRequest(BaseModel):
    amount: Amount | None = None
    receipt: None = None
    airline: None = None
    transfers: None = None
    deal: None = None
