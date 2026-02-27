import json
import os
import sys
from pydantic import BaseModel, Field, ValidationError
from app.logger import get_logger

CONFIG_FILE = "serviceProperties.json"
logger = get_logger("SettingsInit")

# Описываем жесткую структуру конфигурации
class Settings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    files_dir: str = "files"
    ssl_keyfile: str
    ssl_certfile: str
    b24_webhook_url: str = Field(..., description="URL вебхука Bitrix24 обязателен")
    smart_process_settings: dict = {}

def load_config() -> Settings:
    """
    Загружает и валидирует настройки.
    При ошибке валидации приложение завершит работу.
    """
    if not os.path.exists(CONFIG_FILE):
        logger.critical(f"Config file {CONFIG_FILE} not found!")
        sys.exit(1)
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            raw_config = json.load(f)
            
        # Валидация Pydantic
        # Если каких-то полей нет или типы неверные — шлем ошибку валидации
        config = Settings(**raw_config)
        return config
        
    except json.JSONDecodeError as e:
        logger.critical(f"Error decoding JSON config: {e}")
        sys.exit(1)
    except ValidationError as e:
        logger.critical(f"Configuration validation failed:\n{e}")
        sys.exit(1)

# Глобальный объект настроек
settings = load_config()

# Создаем папку для файлов
if not os.path.exists(settings.files_dir):
    try:
        os.makedirs(settings.files_dir)
    except OSError as e:
        logger.critical(f"CRITICAL: Could not create files directory '{settings.files_dir}': {e}")
        sys.exit(1)