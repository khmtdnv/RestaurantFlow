import uuid

import aiohttp
from domain.interfaces.payment_provider import IPaymentProvider


class YookassaAdapter(IPaymentProvider):
    def __init__(self, shop_id: str, secret_key: str, session: aiohttp.ClientSession):
        self._auth = aiohttp.BasicAuth(shop_id, secret_key)
        self._session = session
        self._base_url = "https://api.yookassa.ru/v3/payments"

    async def create_payment(self, amount: float, description: str) -> str:
        headers = {"Idempotence-Key": str(uuid.uuid4())}
        payload = {
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": "..."},
            "description": description,
        }

        async with self._session.post(
            self._base_url, auth=self._auth, json=payload, headers=headers
        ) as response:
            data = await response.json()
            # Обработка ошибок из твоего метода _handle_response
            return data["confirmation"]["confirmation_url"]
