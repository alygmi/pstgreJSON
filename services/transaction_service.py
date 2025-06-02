from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import Request, Query
from typing import List, Dict, Any, Optional
from sqlalchemy import asc, desc
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
    get_sales_data,
    getApiDataExternal
)
from models.models import Transaction
import logging

logger = logging.getLogger(__name__)


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

def fetch_sales_data(
    db: Session, 
    device_id: str, 
    start_ts:Optional[int], 
    end_ts: Optional[int],
    limit: Optional[int] = None,
    sort: Optional[str] = "desc",
    settlement: bool = False
    ):
    transactions = get_sales_data(db, device_id, start_ts, end_ts, limit, sort, settlement)

    result = []
    for t in transactions:
        product = t.product_detail or {}
        # name = product.get("product", {}).get("name", "")
        # sku = product.get("product", {}).get("sku", "")
        row = {
            "name": product.get("name", ""),
            "sku": product.get("sku", ""),
            "gross_amount": str(t.amount),
            "quantity": str(product.get("quantity", "1")),
            "transaction_time": datetime.fromtimestamp(t.ts / 1000).strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_status": t.status
        }
        result.append(row)

    return{"sale" : result}

# def convert_timestamp_to_datetime(ts: int) -> str:
#     dt = datetime.fromtimestamp(ts / 1000)
#     return dt.strftime("%Y-%m-%d %H:%M:%S")

# async def getMachineData() -> dict:
#     raw_data = await getApiDataExternal()

#     print("RAW DATA:", raw_data)

#     if not raw_data:
#         raise ValueError("Data kosong dari API")

#     first_item = raw_data[0]  # karena hasilnya list

#     online_data = first_item.get("online", {})  # aman karena dict
#     is_online = online_data.get("is_online", False)
#     last_online_ts = online_data.get("last_online_ts")

#     formatted_data = {
#         "id": str(first_item.get("id", "")),
#         "code": first_item.get("serial_number", ""),
#         "name": first_item.get("name", ""),
#         "last_online": convert_timestamp_to_datetime(last_online_ts) if last_online_ts else None,
#         "status": "online" if is_online else "offline"
#     }

#     print("DATA AKAN DIKEMBALIKAN:", formatted_data)

#     return formatted_data

def convert_timestamp_to_datetime(ts: int) -> str:
    """Konversi timestamp (ms) ke string datetime."""
    if not isinstance(ts, (int, float)) or ts <= 0:
        raise ValueError("Timestamp harus berupa angka positif")
    try:
        dt = datetime.fromtimestamp(ts / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (OverflowError, OSError) as e:
        raise ValueError(f"Gagal konversi timestamp: {str(e)}")

async def getMachineData() -> dict:
    try:
        raw_data = await getApiDataExternal()
        print(f"Total raw data items: {len(raw_data)}")  # Debug: cek jumlah data

        if not raw_data or not isinstance(raw_data, list):
            raise ValueError("Data devices kosong atau tidak valid")

        result = []
        for device in raw_data:
            if not isinstance(device, dict):  # Pastikan tiap device adalah dict
                print(f"Skipping invalid device: {device}")  # Debug
                continue

            online_data = device.get("online", {})
            
            # Debug: print device yang sedang diproses
            print(f"Processing device: {device.get('id')} - {device.get('serial_number')}")
            
            transformed = {
                "id": str(device.get("id", "")),
                "code": device.get("serial_number", ""),
                "name": device.get("name", ""),
                "last_online": convert_timestamp_to_datetime(online_data.get("last_online_ts")) 
                             if online_data.get("last_online_ts") else None,
                "status": "online" if online_data.get("is_online", False) else "offline"
            }
            result.append(transformed)

        print(f"Total transformed items: {len(result)}")  # Debug
        return {"result": result}

    except Exception as e:
        print(f"Error in processing: {str(e)}")  # Debug
        raise ValueError(f"Gagal memproses data: {str(e)}")

