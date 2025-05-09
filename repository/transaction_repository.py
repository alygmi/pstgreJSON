# transaction_repository.py
from sqlalchemy.orm import Session
from typing import Optional
from models.models import Transaction
from schemas.schemas import TransactionCreate
import logging

logger = logging.getLogger(__name__)


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_transaction(self, transaction_data: TransactionCreate) -> Optional[str]:
        """
        Menyimpan data transaksi ke database
        Args:
            transaction_data: Data transaksi yang sudah divalidasi (TransactionCreate)
        Returns:
            str: ID transaksi jika berhasil
            None: Jika gagal menyimpan
        """
        try:
            db_transaction = Transaction(**transaction_data.dict())

            self.db.add(db_transaction)
            self.db.commit()
            self.db.refresh(db_transaction)

            logger.info(f"Transaction saved successfully: {db_transaction.id}")
            return db_transaction.id

        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Failed to save transaction: {str(e)}", exc_info=True)
            return None

    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Mendapatkan transaksi berdasarkan ID
        Args:
            transaction_id: ID transaksi
        Returns:
            Transaction: Objek transaksi jika ditemukan
            None: Jika tidak ditemukan
        """
        try:
            return self.db.query(Transaction)\
                       .filter(Transaction.id == transaction_id)\
                       .first()
        except Exception as e:
            logger.error(
                f"Error fetching transaction {transaction_id}: {str(e)}", exc_info=True)
            return None

    def get_transactions_by_time_range(self, start: int, end: int) -> list[Transaction]:
        """
        Mendapatkan transaksi dalam rentang waktu tertentu
        Args:
            start: Timestamp awal (unix timestamp)
            end: Timestamp akhir (unix timestamp)
        Returns:
            list[Transaction]: Daftar transaksi
        """
        try:
            return self.db.query(Transaction)\
                       .filter(Transaction.ts >= start, Transaction.ts <= end)\
                       .order_by(Transaction.ts.desc())\
                       .all()
        except Exception as e:
            logger.error(
                f"Error fetching transactions by time range: {str(e)}", exc_info=True)
            return []
