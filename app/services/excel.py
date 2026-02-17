import os
from openpyxl import Workbook
from app.config import settings
from app.logger import get_logger

logger = get_logger("ExcelService")

def create_deal_report(smart_process_id: int, deals_data: list) -> str:
    """
    Создает Excel файл на основе данных сделок и помещает его в каталог файлов.
    Возвращает имя созданного файла.
    """
    try:
        filename = f"ticket_register_{smart_process_id}.xlsx"
        filepath = os.path.join(settings.files_dir, filename)

        wb = Workbook()
        ws = wb.active
        ws.title = f"Реестр билетов №{smart_process_id}"

        # Формируем заголовки
        headers = []
        for key, value in deals_data[0].items():
            headers.append(key)

        # Записываем заголовки в Excel
        ws.append(headers) # 1-я строка

        # Обходим и пишем строки из данных сделок
        for deal_data in deals_data:
            values = []
            for key, value in deal_data.items():
                # Приводим к строке, чтобы Excel не ругался на сложные типы (если они есть)
                values.append(str(value) if value is not None else "")
            ws.append(values)

        wb.save(filepath)
        logger.info(f"Excel report created: {filepath}")
        
        return filename

    except Exception as e:
        logger.error(f"Failed to create Excel report: {e}")
        raise e