from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.v1.schemas import *
from app.logger import get_logger
from app.services.workflow import process_smart_event

router = APIRouter()
logger = get_logger("API_v1")

@router.get("/test", response_model=TestResponse)
async def test_echo(text: str = "default"):
    return {"status": "success", "version": "v1", "received_data": text}

@router.post("/test", response_model=TestResponse)
async def test_echo(payload: Optional[TestResponse] = None):
    return {"status": "success", "version": "v1", "received_data": payload}

@router.get("/sendDealData", response_model=SmartProcessResponse)
async def send_deal_data_get(
    smart_type_id: int = Query(..., description="ID типа смарт-процесса"),
    smart_process_id: int = Query(..., description="ID смарт-процесса")):
    try:
        result = await process_smart_event(smart_type_id, smart_process_id)
        return result
    except Exception as e:
        logger.error(f"Error in GET /sendDealData: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sendDealData", response_model=SmartProcessResponse)
async def send_deal_data_post(
    payload: Optional[SmartProcessWebhook] = None,
    smart_type_id: Optional[int] = Query(None, alias="smart_type_id", description="ID типа смарт-процесса"),
    smart_process_id: Optional[int] = Query(None, alias="smart_process_id", description="ID смарт-процесса"),
    bitrix_raw_id: BitrixForm = Depends()):

    if bitrix_raw_id:
        logger.debug(f"Raw Bitrix24 income data: {bitrix_raw_id}")

    q_smart_type_id = smart_type_id or (payload.smart_type_id if payload else None)
    q_smart_process_id = smart_process_id or (payload.smart_process_id if payload else None)
    if not q_smart_type_id:
        raise HTTPException(status_code=400, detail="smart_type_id is missing in both Body and Query params")
    elif not q_smart_process_id:
        raise HTTPException(status_code=400, detail="smart_process_id is missing in both Body and Query params")

    try:
        result = await process_smart_event(q_smart_type_id, q_smart_process_id)
        return result
    except Exception as e:
        logger.error(f"Error in POST /sendDealData: {e}")
        raise HTTPException(status_code=500, detail=str(e))