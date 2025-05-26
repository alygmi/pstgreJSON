from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import Request
from typing import List
from utils.transaction_utils import build_transaction_dict
from schemas.schemas import (
    TransactionById,
    TransactionByPayment,
    TransactionByStatus,
    TransactionCreate,
    TsRangeRequest,
    TransactionUpdate,
    TransactionOut
)
from repository.transaction_repo import (
    get_transactions_by_ts_range,
    save_transaction,
    fetch_transaction_by_id,
    fetch_transaction_by_status,
    fetch_transaction_by_payment,
    update_trans_by_ts,
    refund_approval_by_ts,
    get_sales_data
)
from models.models import Transaction


async def process_transaction(request: Request, db: Session):
    data = await request.json()
    transaction_dict = build_transaction_dict(data)
    transaction_data = TransactionCreate(**transaction_dict)
    db_transaction = Transaction(**transaction_data.dict())
    save_transaction(db, db_transaction)
    return {"status": "success", "transaction_id": transaction_data.id}


def update_transaction(ts: int, updates: TransactionUpdate, db: Session):
    return update_trans_by_ts(ts, updates, db)

def refund_transaction(ts: int, db: Session):
    return refund_approval_by_ts(ts, db)


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

def fetch_sales_data(db: Session, device_id: str, start_ts:int, end_ts: int):
    transactions = get_sales_data(db, device_id, start_ts, end_ts)

    result = []
    for t in transactions:
        product = t.product_detail or {}
        name = product.get("product", {}).get("name", "")
        sku = product.get("product", {}).get("sku", "")
        row = [
            name,
            sku,
            str(t.amount),
            str(product.get("quantity", "1")),
            datetime.fromtimestamp(t.ts / 1000).strftime("%Y-%m-%d %H:%M:%S"),
            t.status
        ]
        result.append(row)

    return{"sale" : result}

