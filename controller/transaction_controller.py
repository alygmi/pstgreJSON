from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List

from models.models import Transaction
from schemas.schemas import (
    TransactionById,
    TransactionByPayment,
    TransactionByStatus,
    TransactionCreate,
    TsRangeRequest,
    TransactionUpdate
)
from services.transaction_service import (
    get_transactions_by_id,
    get_transactions_by_payment,
    get_transactions_by_status,
    get_transactions_by_ts,
    process_transaction,
    update_transaction,
    refund_transaction
)
from database import get_db

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

