import httpx
from app.config import settings
from app.logger import get_logger

logger = get_logger("BitrixService")

class BitrixClient:
    def __init__(self):
        self.webhook_url = settings.b24_webhook_url
        if not self.webhook_url:
            logger.critical("Bitrix24 Webhook URL is missing in configuration!")

    async def get_deal(self, deal_id: int) -> dict:
        """
        Получает информацию о сделке по ID из Bitrix24.
        Метод API: crm.deal.get
        """
        if not self.webhook_url:
            logger.critical("Bitrix24 Webhook URL is not configured")
            raise ValueError("Bitrix24 Webhook URL is not configured")

        method = "crm.deal.get"
        url = f"{self.webhook_url}/{method}"
        
        params = {
            "ID": deal_id
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                
                # Проверка на логические ошибки от Битрикса (например, сделка не найдена)
                if "error" in data:
                    error_msg = data.get("error_description", "Unknown Bitrix error")
                    logger.error(f"Bitrix API Error: {error_msg}")
                    raise Exception(f"Bitrix API Error: {error_msg}")

                result = data.get("result", {})
                logger.info(f"Successfully fetched deal {deal_id}. Title: {result.get('TITLE')}")
                return result

            except httpx.RequestError as e:
                logger.error(f"Network error while connecting to Bitrix24: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from Bitrix24: {e}")
                raise

# Создаем экземпляр клиента
bitrix_client = BitrixClient()