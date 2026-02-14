from pydantic import BaseModel
from typing import Dict, Any, Optional

class DealWebhook(BaseModel):
    deal_id: int

class DealResponse(BaseModel):
    status: str
    message: str
    deal_id: int
    download_url: Optional[str] = None
    bitrix_data: Optional[Dict[str, Any]] = None