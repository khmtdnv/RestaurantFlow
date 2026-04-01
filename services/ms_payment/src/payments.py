import asyncio
import uuid
from typing import Any, Dict, List

import aiohttp
from pydantic import BaseModel, ConfigDict


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


class PaymentConfirmRequest(BaseModel):
    amount: Amount | None = None
    receipt: None = None
    airline: None = None
    transfers: None = None
    deal: None = None


SHOP_ID = "1317278"
SECRET_KEY = "test_ObkuzWlKa4FBH2zgkQZU4IBicD7g3v1U_dKCO4dfysI"


class PaymentServiceException(BaseModel):
    type: str
    id: str
    code: str
    description: str
    parameter: str | None = None


class YookassaException(Exception):
    pass


class InvalidRequest(YookassaException):
    pass


class InvalidCredentials(YookassaException):
    pass


class Forbidden(YookassaException):
    pass


class NotFound(YookassaException):
    pass


class UnsupportedMethod(YookassaException):
    pass


class UnsupportedContentType(YookassaException):
    pass


class RequestsLimit(YookassaException):
    pass


class PaymentService:
    def __init__(self, http_client: aiohttp.ClientSession):
        self.client = http_client
        self.headers = {
            "Idempotence-Key": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }
        self.auth = aiohttp.BasicAuth(login=SHOP_ID, password=SECRET_KEY)
        self.base_url = "https://api.yookassa.ru/v3/payments"

    async def _handle_response(self, response: aiohttp.ClientResponse):
        data = await response.json()

        if response.status == 200:
            return data
        elif response.status == 400:
            data = PaymentServiceException.model_validate(data)
            raise InvalidRequest(
                f"Неправильный запрос, нарушен синтаксис или логика запроса.\n{data}"
            )
        elif response.status == 401:
            data = PaymentServiceException.model_validate(data)
            raise InvalidCredentials(f"Некорректные данные для аутентификации запроса.\n{data}")
        elif response.status == 403:
            data = PaymentServiceException.model_validate(data)
            raise Forbidden(f"Не хватает прав для совершения операции.\n{data}")
        elif response.status == 404:
            data = PaymentServiceException.model_validate(data)
            raise NotFound(f"Запрашиваемый ресурс не найден.\n{data}")
        elif response.status == 405:
            raise UnsupportedMethod("Некорректный HTTP-метод запроса.")
        elif response.status == 415:
            raise UnsupportedContentType("Некорректный тип контента для POST-запроса.")
        elif response.status == 429:
            data = PaymentServiceException.model_validate(data)
            raise RequestsLimit(f"Превышен лимит запросов в единицу времени.\n{data}")
        elif response.status == 500:
            data = PaymentServiceException.model_validate(data)
            raise RequestsLimit(f"Технические неполадки на стороне ЮKassa.\n{data}")

    async def create_payment(self, payload: PaymentCreateRequest) -> Payment:
        """Создание платежа (POST /payments)"""

        # print(f"payload:\n{payload}")
        # print(f"payload.model_dump():\n{payload.model_dump()}")
        # print(f"payload.model_dump(exclude_none=True):\n{payload.model_dump(exclude_none=True)}")
        async with self.client.post(
            url=self.base_url,
            headers=self.headers,
            auth=self.auth,
            json=payload.model_dump(exclude_none=True),
        ) as response:
            data = await self._handle_response(response)
            return Payment.model_validate(data)

    async def list_payments(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaymentList:
        """Список платежей (GET /payments)"""
        params = {}
        if limit:
            params.update({"limit": limit})
        if cursor:
            params.update({"cursor": cursor})

        async with self.client.get(
            url=self.base_url,
            headers=self.headers,
            auth=self.auth,
            params=params,
        ) as response:
            data = await self._handle_response(response)
            return PaymentList.model_validate(data)

    # GET
    # /payments
    # /{payment_id}
    # Информация о платеже
    async def get_payment(self, payment_id: str) -> Payment:
        """Информация о платеже (GET /payments/{payment_id})"""

        url = f"{self.base_url}/{payment_id}"

        async with self.client.get(url=url, headers=self.headers, auth=self.auth) as response:
            data = await self._handle_response(response)
            return Payment.model_validate(data)

    # POST
    # /payments
    # /{payment_id}
    # /capture
    # Подтверждение платежа
    async def confirm_payment(self, payment_id: str, payload: PaymentConfirmRequest) -> Payment:
        """Подтверждение платежа (POST /payments/{payment_id}/cancel)"""

        url = f"{self.base_url}/{payment_id}/cancel"

        async with self.client.post(
            url=url,
            headers=self.headers,
            auth=self.auth,
            json=payload.model_dump(exclude_none=True),
        ) as response:
            data = await self._handle_response(response)
            return Payment.model_validate(data)

    # POST
    # /payments
    # /{payment_id}
    # /cancel
    # Отмена платежа
    async def cancel_payment(self, payment_id: str) -> Payment:
        """Подтверждение платежа (POST /payments/{payment_id}/capture)"""

        url = f"{self.base_url}/{payment_id}/capture"

        async with self.client.post(url=url, headers=self.headers, auth=self.auth) as response:
            data = await self._handle_response(response)
            return Payment.model_validate(data)


async def main():
    http_client = aiohttp.ClientSession()
    amount = Amount(value="100.00", currency="RUB")
    # Оплата по СБП
    sbp_yookassa = PaymentCreateRequest(  # noqa
        amount=amount,
        payment_method_data=PaymentMethodData(type="sbp"),
        confirmation=Confirmation(),
        capture=True,
        description="SBP",
    )
    # Оплата по карте (ЮКасса возвращает ссылку на страницу оплаты с вводом данных карты)
    card_yookassa = PaymentCreateRequest(  # noqa
        amount=amount,
        payment_method_data=PaymentMethodData(type="bank_card"),
        confirmation=Confirmation(),
        capture=False,
        description="BANK CARD + 3DS",
    )
    # Оплата по карте (ЮКасса возвращает ссылку на страницу с 3DSecure, данные карты нужно собрать самостоятельно)
    card_selfhosted = PaymentCreateRequest(  # noqa
        amount=amount,
        payment_method_data=PaymentMethodData(
            type="bank_card",
            card=Card(
                number="5555555555554477",
                expiry_year="2031",
                expiry_month="11",
            ),
        ),
        confirmation=Confirmation(),
        capture=False,
        description="3DS ONLY",
    )

    confirm_payment_data = PaymentConfirmRequest(amount=amount)  # noqa

    service = PaymentService(http_client)  # noqa
    # try:
    # 1. create
    # result = await service.create_payment(payload=card_selfhosted)
    # if result.confirmation:
    #     print(result.confirmation.confirmation_url)

    # 2. list
    # result = await service.list_payments()
    # print(result)
    # cursor = result.next_cursor
    # while cursor:
    #     result = await service.list_payments(cursor=cursor)
    #     cursor = result.next_cursor

    # 3. get
    # payment_id = "315e174b-000f-5001-8000-1b15a4ff1881"
    # result = await service.get_payment(payment_id)
    # print(result)

    # 4. confirm
    # payment_id = "315e2594-000f-5000-b000-19f56475f0f3"
    # result = await service.confirm_payment(payment_id=payment_id, payload=confirm_payment_data)
    # print(result)

    # 5. confirm
    # payment_id = "315e2594-000f-5000-b000-19f56475f0f3"
    # result = await service.cancel_payment(payment_id=payment_id)
    # print(result)

    # except Exception as e:
    #     print(e)

    await http_client.close()


if __name__ == "__main__":
    asyncio.run(main())
