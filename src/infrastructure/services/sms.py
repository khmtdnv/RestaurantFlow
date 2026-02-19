from src.application.interfaces import AbstractSMSService


class DummySMSService(AbstractSMSService):
    async def send_sms(self, phone: str, code: str):
        print(f"--- Отправка SMS на {phone}: ваш код {code} ---")
