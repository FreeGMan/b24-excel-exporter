from pydantic import BaseModel
from typing import Optional
from fastapi import Form

class TestReqest(BaseModel):
    status: str
    version: str
    received_data: str

class TestResponse(BaseModel):
    msg: Optional[str] = "" 

class SmartProcessWebhook(BaseModel):
    smart_type_id: int
    smart_process_id: int

class SmartProcessResponse(BaseModel):
    status: str
    message: str
    smart_type_id: Optional[int] = None
    smart_process_id: Optional[int] = None
    download_url: Optional[str] = None

class BitrixForm:
    """
    Класс для обработки Form Data от Bitrix24
    """
    def __init__(
        self,
        document_id: Optional[str] = Form(
            None, 
            alias="document_id[2]", 
            description="Сырой ID из вебхука Bitrix (например: DYNAMIC_1040_50)"
        )
    ):
        self.raw_id = document_id