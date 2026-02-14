import logging
import sys

# Формат логов: Время - Имя модуля - Уровень - Сообщение
LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Проверка, чтобы не дублировать хендлеры при перезагрузке
    if not logger.handlers:
        # Вывод в консоль (stdout)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger