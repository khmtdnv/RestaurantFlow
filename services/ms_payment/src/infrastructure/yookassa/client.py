import uuid

import aiohttp
from infrastructure.yookassa.schemas import (
    Payment,
    PaymentConfirmRequest,
    PaymentCreateRequest,
    PaymentList,
    PaymentServiceException,
)


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


class YookassaClient:
    def __init__(
        self, http_client: aiohttp.ClientSession, base_url: str, shop_id: str, secret_key: str
    ):
        self.client = http_client
        self.base_url = base_url  # URL передаем из конфига (чтобы легко подменить на мок)
        self.auth = aiohttp.BasicAuth(login=shop_id, password=secret_key)
        self.headers = {
            "Idempotence-Key": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }

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
