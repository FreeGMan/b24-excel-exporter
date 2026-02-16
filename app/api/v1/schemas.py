from pydantic import BaseModel
from typing import Dict, Any, Optional

class TestReqest(BaseModel):
    status: str
    version: str
    received_data: str

class TestResponse(BaseModel):
    msg: Optional[str] = "" 

class SmartProcessWebhook(BaseModel):
    smart_process_id: int

class SmartProcessResponse(BaseModel):
    status: str
    message: str
    smart_process_id: Optional[int] = None
    download_url: Optional[str] = None