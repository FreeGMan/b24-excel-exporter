import os
from app.services.bitrix import bitrix_client
from app.services.excel import create_deal_report
from app.config import settings
from app.logger import get_logger

logger = get_logger("WorkflowService")

async def process_smart_event(smart_process_id: int) -> dict:
    """
    Полный цикл: Bitrix -> Excel -> Link
    """
    logger.info(f"Start processing workflow for smart-process ID: {smart_process_id}")
    
    # 1. Получаем массив сделок из смарт-процесса
    deals_ids = await bitrix_client.get_deals_from_sp(smart_process_id)
    if not deals_ids:
        logger.warning(f"Deals array for smart-process {smart_process_id} was empty")
        return {
            "status": "warning",
            "message": f"Deals array for smart-process {smart_process_id} was empty",
            "smart_process_id": smart_process_id
        }   
    
    # 2. Получаем данные полей сделок
    deals_data = await bitrix_client.get_deals(deals_ids)
    if not deals_data:
        logger.warning("Deals data array was empty")
        return {
            "status": "warning",
            "message": "Deals data array was empty",
            "smart_process_id": smart_process_id
        }   

    # 3. Формируем Excel файл
    filename = create_deal_report(smart_process_id, deals_data)
    
    # 4. Отправляем файл в коммент к смарт-процессу
    await bitrix_client.send_file_as_comment_to_timeline(
        f"dynamic_{settings.smart_process_type_id}", # Для комментариев в таймлайне, тип объекта смарт-процесса не просто его ID
        smart_process_id,
        os.path.join(settings.files_dir, filename)
    ) 
    
    # 5. Формируем прямую ссылку на скачивание
    protocol = "https" 
    download_url = f"{protocol}://{settings.host}:{settings.port}/{settings.files_dir}/{filename}"
    
    logger.info(f"Workflow completed. File available at: {download_url}")

    return {
        "status": "success",
        "message": "Deal processed and Excel generated",
        "smart_process_id": smart_process_id,
        "download_url": download_url
    }