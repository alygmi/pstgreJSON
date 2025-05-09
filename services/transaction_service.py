from sqlalchemy.orm import Session
from fastapi import Request
from typing import List
from utils.transaction_utils import build_transaction_dict
from schemas.schemas import TransactionById, TransactionByPayment, TransactionByStatus, TransactionCreate, TsRangeRequest
from repository.transaction_repo import (
    get_transactions_by_ts_range,
    save_transaction,
    fetch_transaction_by_id,
    fetch_transaction_by_status,
    fetch_transaction_by_payment
)
from models.models import Transaction


async def process_transaction(request: Request, db: Session):
    data = await request.json()
    transaction_dict = build_transaction_dict(data)
    transaction_data = TransactionCreate(**transaction_dict)
    db_transaction = Transaction(**transaction_data.dict())
    save_transaction(db, db_transaction)
    return {"status": "success", "transaction_id": transaction_data.id}


def fetch_transactions_by_ts_range(
    db: Session,
    ts_start=None,
    ts_end=None
) -> List[TransactionCreate]:
    transactions = get_transactions_by_ts_range(db, ts_start, ts_end)
    if not transactions:
        return []
    return [TransactionCreate(**t.__dict__) for t in transactions]


async def get_transactions_by_ts(db: Session, payload: TsRangeRequest):
    return get_transactions_by_ts_range(
        db,
        ts_start=payload.ts_start,
        ts_end=payload.ts_end
    )


async def get_transactions_by_id(db: Session, payload: TransactionById):
    return fetch_transaction_by_id(db, payload.id)


async def get_transactions_by_status(db: Session, payload: TransactionByStatus):
    tx_list = fetch_transaction_by_status(db, payload.status)

    return [TransactionCreate(**tx.__dict__) for tx in tx_list] if tx_list else None


async def get_transactions_by_payment(db: Session, payload: TransactionByPayment):
    tx_list = fetch_transaction_by_payment(db, payload.payment_method)

    return [TransactionCreate(**tx.__dict__) for tx in tx_list] if tx_list else None
