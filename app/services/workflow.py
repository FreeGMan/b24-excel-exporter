from app.services.bitrix import bitrix_client
from app.services.excel import create_deal_report
from app.config import settings
from app.logger import get_logger

logger = get_logger("WorkflowService")

async def process_deal_event(deal_id: int) -> dict:
    """
    Полный цикл: Bitrix -> Excel -> Link
    """
    logger.info(f"Start processing workflow for Deal ID: {deal_id}")
    
    # 1. Получаем данные из Bitrix24
    deal_data = await bitrix_client.get_deal(deal_id)
    
    # 2. Формируем Excel файл
    filename = create_deal_report(deal_data)
    
    # 3. Формируем прямую ссылку на скачивание
    protocol = "https" 
    download_url = f"{protocol}://{settings.host}:{settings.port}/{settings.files_dir}/{filename}"
    
    logger.info(f"Workflow completed. File available at: {download_url}")

    return {
        "status": "success",
        "message": "Deal processed and Excel generated",
        "deal_id": deal_id,
        "download_url": download_url,
        "bitrix_data": {
            "ID": deal_data.get("ID"),
            "TITLE": deal_data.get("TITLE"),
            "OPPORTUNITY": deal_data.get("OPPORTUNITY"),
            "CURRENCY_ID": deal_data.get("CURRENCY_ID")
        }
    }