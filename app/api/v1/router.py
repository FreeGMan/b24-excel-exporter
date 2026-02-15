from fastapi import APIRouter, HTTPException, Query
from app.api.v1.schemas import DealWebhook, DealResponse
from app.logger import get_logger
from app.services.workflow import process_deal_event

router = APIRouter()
logger = get_logger("API_v1")

@router.get("/test")
async def test_echo(text: str = "default"):
    return {"status": "success", "version": "v1", "received_text": text}

@router.post("/test")
async def test_echo(payload):
    return {"status": "success", "version": "v1", "received_data": payload}

# --- POST ---
@router.post("/sendDealData", response_model=DealResponse)
async def send_deal_data_post(payload: DealWebhook):
    try:
        result = await process_deal_event(payload.deal_id)
        return result
    except Exception as e:
        logger.error(f"Error in POST /sendDealData: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- GET ---
@router.get("/sendDealData", response_model=DealResponse)
async def send_deal_data_get(deal_id: int = Query(..., description="ID сделки")):
    try:
        result = await process_deal_event(deal_id)
        return result
    except Exception as e:
        logger.error(f"Error in GET /sendDealData: {e}")
        raise HTTPException(status_code=500, detail=str(e))