from fastapi import APIRouter, HTTPException, Query
from app.api.v1.schemas import *
from app.logger import get_logger
from app.services.workflow import process_smart_event

router = APIRouter()
logger = get_logger("API_v1")

@router.get("/test", response_model=TestResponse)
async def test_echo(text: str = "default"):
    return {"status": "success", "version": "v1", "received_data": text}

@router.post("/test", response_model=TestResponse)
async def test_echo(payload):
    return {"status": "success", "version": "v1", "received_data": payload}

# --- POST ---
@router.post("/sendDealData", response_model=SmartProcessResponse)
async def send_deal_data_post(payload: SmartProcessWebhook):
    try:
        result = await process_smart_event(payload.smart_process_id)
        return result
    except Exception as e:
        logger.error(f"Error in POST /sendDealData: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- GET ---
@router.get("/sendDealData", response_model=SmartProcessResponse)
async def send_deal_data_get(smart_process_id: int = Query(..., description="ID смарт-процесса")):
    try:
        result = await process_smart_event(smart_process_id)
        return result
    except Exception as e:
        logger.error(f"Error in GET /sendDealData: {e}")
        raise HTTPException(status_code=500, detail=str(e))