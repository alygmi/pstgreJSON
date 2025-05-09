from sqlalchemy.orm import Session
from models.models import Transaction


def save_transaction(db: Session, transaction: Transaction):
    db.add(transaction)
    db.commit()
    db.refresh(transaction)


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
