import os
from app.services.bitrix import bitrix_client
from app.services.excel import create_deal_report
from app.config import settings
from app.logger import get_logger

logger = get_logger("WorkflowService")

async def process_smart_event(smart_type_id: int, smart_process_id: int) -> dict:
    """
    Полный цикл: Bitrix -> Excel -> Link -> Bitrix
    """
    logger.info(f"Start processing workflow for smart-process ID: {smart_process_id}")
    
    # 0. Проверяем наличие настроек, для переданного типа смарт-процесса
    if not settings.smart_process_settings.get(f"{smart_type_id}", None):
        logger.warning(f"No setting for smart-process type ID {smart_type_id}")
        return {
            "status": "warning",
            "message": f"No setting for smart-process type ID {smart_type_id}",
            "smart_type_id": smart_type_id,
            "smart_process_id": smart_process_id
        }        

    # 1. Получаем массив сделок из смарт-процесса
    deals_ids = await bitrix_client.get_deals_from_sp(smart_type_id, smart_process_id)
    if not deals_ids:
        logger.warning(f"Deals array for smart-process {smart_process_id} was empty")
        return {
            "status": "warning",
            "message": f"Deals array for smart-process {smart_process_id} was empty",
            "smart_type_id": smart_type_id,
            "smart_process_id": smart_process_id
        }   
    
    # 2. Получаем данные полей сделок
    deals_data = await bitrix_client.get_deals(deals_ids, smart_type_id)
    if not deals_data:
        logger.warning("Deals data array was empty")
        return {
            "status": "warning",
            "message": "Deals data array was empty",
            "smart_type_id": smart_type_id,
            "smart_process_id": smart_process_id
        }

    # 3. Подготавливаем данные для вывода в Excel
    deal_fields = await bitrix_client.get_deal_fields()
    data_for_excel = []
    
    if deal_fields:
        # Первой строкой должны быть имена колонок
        title_row = []
        for key, value in deals_data[0].items():
            field_prop = deal_fields.get(key)
            # Преобразем имена полей в их полные наименования для вывода в заголовки
            if type(field_prop) is dict:
                field_title = field_prop.get("listLabel", field_prop["title"])
            else:
                field_title = f"{key}"
            
            title_row.append(field_title)
        data_for_excel.append(title_row)

        for deal_data in deals_data:
            deal_row = []
            for key, value in deal_data.items():
                final_value = value
                field_prop = deal_fields.get(key)
                
                # Если это списочное поле, то берем значение 
                if field_prop.get("items"):
                    field_values = {item["ID"]: item["VALUE"] for item in field_prop["items"]}
                    final_value = field_values.get(value, value)
                
                deal_row.append(final_value)
            data_for_excel.append(deal_row)       

    # 4. Формируем Excel файл
    filename = create_deal_report(smart_process_id, data_for_excel)
    
    # 5. Отправляем файл в коммент к смарт-процессу
    await bitrix_client.send_file_to_sp(
        smart_type_id,
        smart_process_id,
        os.path.join(settings.files_dir, filename)
    ) 
    
    # 6. Формируем прямую ссылку на скачивание
    protocol = "https" 
    download_url = f"{protocol}://{settings.host}:{settings.port}/{settings.files_dir}/{filename}"
    
    logger.info(f"Workflow completed. File available at: {download_url}")

    return {
        "status": "success",
        "message": "Deal processed and Excel generated",
        "smart_type_id": smart_type_id,
        "smart_process_id": smart_process_id,
        "download_url": download_url
    }