import httpx
from app.config import settings
from app.logger import get_logger

logger = get_logger("BitrixService")

class BitrixClient:
    def __init__(self):
        self.webhook_url = settings.b24_webhook_url
        if not self.webhook_url:
            logger.critical("Bitrix24 Webhook URL is missing in configuration!")        
            raise ValueError("Bitrix24 Webhook URL is missing in configuration!")   

    async def get_deal(self, deal_id: int) -> dict:
        """
        Получает информацию о сделке по ID из Bitrix24.
        Метод API: crm.deal.get
        """
        
        method = "crm.deal.get"
        url = f"{self.webhook_url}/{method}"
        
        params = {
            "id": deal_id
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=params, timeout=10.0)
                response.raise_for_status()
                
                result = result_handler(response.json())
                logger.info(f"Successfully fetched deal {deal_id}. Title: {result.get('TITLE')}")
                return result

            except httpx.RequestError as e:
                logger.error(f"Network error while connecting to Bitrix24: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from Bitrix24: {e}")
                raise

    async def get_deals(self, deals_ids: list[int]) -> dict:
        """
        Получает информацию о сделках по массиву ID из Bitrix24.
        Метод API: crm.deal.list
        """
        
        method = "crm.deal.list"
        url = f"{self.webhook_url}/{method}"
        
        params = {
            "SELECT": ["ID", "TITLE"],
            "FILTER": {
                "@ID": deals_ids
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=params, timeout=10.0)
                response.raise_for_status()
                
                result = result_handler(response.json())
                logger.info(f"Successfully fetched deals {deals_ids} data")
                return result

            except httpx.RequestError as e:
                logger.error(f"Network error while connecting to Bitrix24: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from Bitrix24: {e}")
                raise

    async def get_deals_from_sp(self, smart_process_id: int) -> dict:
        """
        Получает массив сделок из реквизита смарт-процесса по ID из Bitrix24.
        ИД типа смарт-процесса и имя доп реквизита с массимов сделок указываются в файле настроек.
        Метод API: crm.item.get
        """

        method = "crm.item.get"
        url = f"{self.webhook_url}/{method}"
        
        params = {
            "id": smart_process_id,
            "entityTypeId": settings.smart_process_type_id
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=params, timeout=10.0)
                response.raise_for_status()
                
                result = result_handler(response.json())
                item_data = result.get('item')
                logger.info(f"Successfully fetched smart process {smart_process_id}. Title: {item_data.get('title')}")
                
                deals_array = item_data.get(settings.sp_deals_uf, [])
                if deals_array and isinstance(deals_array, list):
                    logger.info(f"Deals array: {deals_array}")
                else:
                    logger.warning(f"Deals array is empty or unreachable")

                return [int(item) for item in deals_array]

            except httpx.RequestError as e:
                logger.error(f"Network error while connecting to Bitrix24: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from Bitrix24: {e}")
                raise

# Создаем экземпляр клиента
bitrix_client = BitrixClient()

def result_handler(data: any) -> any:
    """
    Обрабабатывает полученные данные от API Bitrix24.
    В случае не соответствия ожидаемому типу данных и при возрврате ошибки Bitrix'ом вызывает исключение.
    В случае успеха - возвращает данные из result
    """

    if not isinstance(data, dict):
        logger.critical(f"Unexpected Bitrix API type response: {type(data)}")
        raise Exception(f"Unexpected Bitrix API type response: {type(data)}") 
    elif "error" in data:
        error_msg = data.get("error_description", "Unknown Bitrix error")
        logger.error(f"Bitrix API Error: {error_msg}")
        raise Exception(f"Bitrix API Error: {error_msg}")
    else:
        return data.get("result", {})