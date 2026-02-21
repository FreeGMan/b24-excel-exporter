import os
from openpyxl import Workbook
from app.config import settings
from app.logger import get_logger

logger = get_logger("ExcelService")

def create_deal_report(smart_process_id: int, deals_data: list) -> str:
    """
    Создает Excel файл на основе данных сделок и помещает его в каталог файлов.
    Данные сделок передабются как массив (строки) массивов (значения ячеек в строке массивом).
    Первая строка считается заголовочной.
    Возвращает имя созданного файла.
    """
    try:
        filename = f"ticket_register_{smart_process_id}.xlsx"
        filepath = os.path.join(settings.files_dir, filename)

        wb = Workbook()
        ws = wb.active
        ws.title = f"Реестр билетов №{smart_process_id}"

        for deal_data in deals_data:
            ws.append(deal_data)

        wb.save(filepath)
        logger.info(f"Excel report created: {filepath}")
        
        return filename

    except Exception as e:
        logger.error(f"Failed to create Excel report: {e}")
        raise e