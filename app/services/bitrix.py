import httpx
import base64
import os
from app.config import settings
from app.logger import get_logger

logger = get_logger("BitrixService")

class BitrixClient:
    def __init__(self):
        self.webhook_url = settings.b24_webhook_url
        if not self.webhook_url:
            logger.critical("Bitrix24 Webhook URL is missing in configuration!")        
            raise ValueError("Bitrix24 Webhook URL is missing in configuration!")   

    async def get_deal_fields(self) -> dict:
        """
        Возвращает описание полей сделки, в том числе пользовательских из Bitrix24.
        Метод API: crm.deal.fields
        """
        
        method = "crm.deal.fields"
        url = f"{self.webhook_url}/{method}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, timeout=10.0)
                response.raise_for_status()
                
                return result_handler(response.json())

            except httpx.RequestError as e:
                logger.error(f"Network error while connecting to Bitrix24: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from Bitrix24: {e}")
                raise

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

    async def get_deals(self, deals_ids: list[int], smart_type_id: int) -> dict:
        """
        Получает информацию о сделках по массиву ID из Bitrix24.
        Метод API: crm.deal.list
        """
        
        method = "crm.deal.list"
        url = f"{self.webhook_url}/{method}"
        
        smart_process_settings = settings.smart_process_settings.get(f"{smart_type_id}", {})
        deals_fields_for_report = smart_process_settings.get("deals_fields_for_report", [])
        
        params = {
            "SELECT": deals_fields_for_report,
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

    async def get_deals_from_sp(self, smart_type_id: int, smart_process_id: int) -> dict:
        """
        Получает массив сделок из реквизита смарт-процесса по ID из Bitrix24.
        Имя доп реквизита с массивом сделок указываются в файле настроек для каждого ID типа смарт-процесса.
        Метод API: crm.item.get
        """

        method = "crm.item.get"
        url = f"{self.webhook_url}/{method}"
        smart_process_settings = settings.smart_process_settings.get(f"{smart_type_id}", {})
        deals_uf = smart_process_settings.get("deals_uf", None)

        params = {
            "id": smart_process_id,
            "entityTypeId": smart_type_id
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=params, timeout=10.0)
                response.raise_for_status()
                
                result = result_handler(response.json())
                item_data = result.get('item')
                logger.info(f"Successfully fetched SP type ID {smart_type_id} and SP ID {smart_process_id}. Title: {item_data.get('title')}")
                
                deals_array = item_data.get(deals_uf, [])
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

    async def send_file_as_comment_to_timeline(self, etity_type: str, etity_id: int, file_path: str) -> dict:
        """
        Отправляет файл в комментарий таймлайна.
        Метод API: crm.timeline.comment.add
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)

        # 1. Читаем файл и кодируем в Base64
        try:
            with open(file_path, "rb") as file:
                file_content = file.read()
                # Кодируем байты в b64-bytes, затем декодируем в строку (utf-8) для JSON
                encoded_string = base64.b64encode(file_content).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding file to base64: {e}")
            raise

        # 2. Формируем
        method = "crm.timeline.comment.add"
        url = f"{self.webhook_url}/{method}"

        params = {
            "fields": {
                "ENTITY_ID": etity_id,
                "ENTITY_TYPE": etity_type,
                "COMMENT": f"Файл успешно сформирован",
                "FILES": [
                    [filename, encoded_string]
                ]
            }
        }

        # 3. Отправляем
        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Sending file {filename} to Bitrix24 to {etity_id}...")
                response = await client.post(url, json=params, timeout=30.0) # Таймаут побольше для файлов
                response.raise_for_status()
                
                result = result_handler(response.json())
                logger.info(f"Successfully sent file to timeline. Comment ID: {result}")
                return result

            except httpx.RequestError as e:
                logger.error(f"Network error while sending file to Bitrix24: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from Bitrix24 (send file): {e}")
                raise

# Создаем экземпляр клиента
bitrix_client = BitrixClient()

def result_handler(data: any) -> dict:
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