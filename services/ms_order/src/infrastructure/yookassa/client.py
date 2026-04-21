import logging
from decimal import Decimal

import aiohttp
from domain.interfaces.payment_client import IPaymentClient

log = logging.getLogger(__name__)


class PaymentClient(IPaymentClient):
    def __init__(self, base_url: str, session: aiohttp.ClientSession):
        self.base_url = base_url
        self.session = session

    async def create_payment(self, order_id: str, amount: Decimal) -> str | None:
        url = f"{self.base_url}/payments"

        log.info(f"url:{url}")
        payload = {"order_id": str(order_id), "amount": str(amount)}

        try:
            timeout = aiohttp.ClientTimeout(total=5)

            async with self.session.post(url, json=payload, timeout=timeout) as response:
                if response.status in (200, 201):
                    data = await response.json()
                    return data.get("payment_url")
                else:
                    log.warning(f"Неуспешный ответ от ms_payment. Status: {response.status}")
                    return None
        except aiohttp.ClientError as e:
            log.error(f"Ошибка сети при обращении к ms_payment: {e}")
            return None
        except Exception:
            log.exception("Неизвестная ошибка при генерации платежа")
            return None
