from pydantic import BaseModel
from typing import Dict, Any, Optional

class SmartProcessWebhook(BaseModel):
    smart_process_id: int

class SmartProcessResponse(BaseModel):
    status: str
    message: str
    smart_process_id: Optional[int] = None
    download_url: Optional[str] = None
    bitrix_data: Optional[Dict[str, Any]] = None