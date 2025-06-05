from fastapi import (
    APIRouter,
    Depends,
    HTTPException, 
    Query, 
    Request, 
    Form
    )
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import asc, desc
import logging

from models.models import Transaction
from schemas.schemas import (
    TransactionById,
    TransactionByPayment,
    TransactionByStatus,
    TransactionCreate,
    TsRangeRequest,
    TransactionUpdate,
    TransactionOut
)
from services.transaction_service import (
    get_transactions_by_id,
    get_transactions_by_payment,
    get_transactions_by_status,
    get_transactions_by_ts,
    process_transaction,
    update_transaction,
    refund_transaction,
    fetch_sales_data,
    getMachineData,
    process_order
)
from database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/transactions/")
async def create_transaction(request: Request, db: Session = Depends(get_db)):
    try:
        return await process_transaction(request, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transactions/bytsrange", response_model=List[TransactionCreate])
async def get_trans_by_ts_range(
    payload: TsRangeRequest,
    db: Session = Depends(get_db)
):
    return await get_transactions_by_ts(db, payload)


@router.post("/transactions/byid", response_model=TransactionCreate)
async def get_by_id(payload: TransactionById, db: Session = Depends(get_db)):
    transaction = await get_transactions_by_id(db, payload)
    if not transaction:
        raise HTTPException(status_code=404, detail="not found!")
    return transaction


@router.post("/transactions/bystatus", response_model=List[TransactionCreate])
async def get_by_status(payload: TransactionByStatus, db: Session = Depends(get_db)):
    transaction = await get_transactions_by_status(db, payload)
    if not transaction:
        raise HTTPException(status_code=404, detail="not found!")
    return transaction


@router.post("/transactions/bypayment", response_model=List[TransactionCreate])
async def get_by_payment(payload: TransactionByPayment, db: Session = Depends(get_db)):
    transaction = await get_transactions_by_payment(db, payload)
    if not transaction:
        raise HTTPException(status_code=404, detail="not Found!")
    return transaction


@router.get("/transactions/get", response_model=List[TransactionCreate])
def get_trans(
    limit: int = Query(10, ge=1),
    offset: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).offset(offset).limit(limit)
    return transaction


@router.put("/transactions/{ts}")
def update_trans_endpoint(ts: int, updates: TransactionUpdate, db: Session = Depends(get_db)):

    print("Looking for ts:", ts)
    updated = update_transaction(ts, updates, db)

    if not updated:
        raise HTTPException(status_code=404, detail="Transaction Not Found")

    return {"status": "success", "update_transaction": updated}

@router.put("/transactions/refund/{ts}")
def refund_by_ts(ts: int, db: Session = Depends(get_db)):

    refunded = refund_transaction(ts, db)

    if not refunded:
        raise HTTPException(status_code=404, detail="Transaction Not Found")

    return {"status": "success", "refund_transaction": refunded}

@router.post("/transactions/Apireport/SaleCheck")
def get_data_sales(
    db: Session = Depends(get_db),
    device_id: str = Form(...),
    ts_start: Optional[int] = Form(None),
    ts_end: Optional[int] = Form(None),
    sort: Optional[str] = Form("desc"),
    limit: Optional[int] = Form(None),
    settlement: Optional[bool] = Form(False)
):

    return fetch_sales_data(db, device_id, ts_start, ts_end, limit, sort, settlement)

@router.get("/transactions/Apireport/Machinecheck")
async def get_machine_check():
    try:
        result = await getMachineData()
        return result
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/transactions/veem/order")
async def create_order(request: Request, db: Session = Depends(get_db)):
    try:
        return await process_order(request, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 