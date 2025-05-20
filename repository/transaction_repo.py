from sqlalchemy.orm import Session
from models.models import Transaction
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, DataError, ProgrammingError
from schemas.schemas import TransactionUpdate

import time


def save_transaction(db: Session, transaction: Transaction):
    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Gagal menyimpan: mungkin ada duplikasi atau key tidak valid.")
    except DataError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Gagal menyimpan:format atau tipe data tidak sesuai.")
    except ProgrammingError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Gagal menyimpan: error pada sintaks SQL.")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error tidak dikenal: {str(e)}")


def update_trans_by_ts(ts: int, updates: TransactionUpdate, db: Session):
    try:
        transaction = db.query(Transaction).filter(
            Transaction.ts == ts).first()
        if not transaction:
            return None

        update_data = updates.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(transaction, key, value)

        db.commit()
        db.refresh(transaction)
        return transaction
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Gagal menyimpan: mungkin ada duplikasi atau key tidak valid.")
    except DataError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Gagal menyimpan:format atau tipe data tidak sesuai.")
    except ProgrammingError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Gagal menyimpan: error pada sintaks SQL.")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error tidak dikenal: {str(e)}")

def refund_approval_by_ts(ts: int, db: Session):
    try:
        transaction = db.query(Transaction).filter(Transaction.ts == ts).first()

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Epoch generator (milidetik)
        now_epoch = int(time.time() * 1000)

        # Ambil existing refund_detail, atau kosongkan
        refund_detail = transaction.refund_detail or {}

        if refund_detail.get("approval"):
            raise HTTPException(status_code=400, detail="Transaction already refunded!")

        # Set detail refund
        refund_detail["refund_request_ts"] = now_epoch
        refund_detail["approval"] = True

        # Simpan ke DB
        transaction.refund_detail = refund_detail
        db.commit()
        db.refresh(transaction)

        return transaction

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Gagal menyimpan: duplikasi atau key tidak valid.")
    except DataError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Gagal menyimpan: format atau tipe data tidak sesuai.")
    except ProgrammingError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Gagal menyimpan: error pada sintaks SQL.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error tidak dikenal: {str(e)}")



def get_transactions_by_ts_range(
    db: Session,
    ts_start: int = None,
    ts_end: int = None
):
    query = db.query(Transaction)

    if ts_start is not None:
        query = query.filter(Transaction.ts >= ts_start)
    if ts_end is not None:
        query = query.filter(Transaction.ts <= ts_end)

    return query.order_by(Transaction.ts.desc()).all()


def fetch_transaction_by_id(db: Session, id: str):
    return db.query(Transaction).filter(Transaction.id == id).first()


def fetch_transaction_by_status(db: Session, status: str):
    return db.query(Transaction).filter(Transaction.status == status).all()


def fetch_transaction_by_payment(db: Session, payment_method: str):
    return db.query(Transaction).filter(Transaction.payment_method == payment_method).all()
