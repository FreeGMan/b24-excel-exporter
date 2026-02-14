import os
from openpyxl import Workbook
from app.config import settings
from app.logger import get_logger

logger = get_logger("ExcelService")

def create_deal_report(deal_data: dict) -> str:
    """
    Создает Excel файл на основе данных сделки.
    Возвращает имя созданного файла.
    """
    try:
        deal_id = deal_data.get("ID", "unknown")
        filename = f"deal_{deal_id}.xlsx"
        filepath = os.path.join(settings.files_dir, filename)

        wb = Workbook()
        ws = wb.active
        ws.title = f"Deal {deal_id}"

        # Формируем заголовки и строку данных
        # Bitrix возвращает много полей, можно фильтровать, но пока запишем всё плоским списком
        headers = []
        values = []

        for key, value in deal_data.items():
            headers.append(key)
            # Приводим к строке, чтобы Excel не ругался на сложные типы (если они есть)
            values.append(str(value) if value is not None else "")

        # Записываем в Excel
        ws.append(headers) # 1-я строка
        ws.append(values)  # 2-я строка

        wb.save(filepath)
        logger.info(f"Excel report created: {filepath}")
        
        return filename

    except Exception as e:
        logger.error(f"Failed to create Excel report: {e}")
        raise e