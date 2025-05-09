from services.transaction_service import fetch_transactions_by_ts_range
from schemas.schemas import TransactionCreate, TsRangeRequest
from repository.transaction_repo import get_transactions_by_ts_range
from models.models import Transaction
from database import get_db
from controller import transaction_controller
from decimal import Decimal
from typing import List, Optional
from fastapi import FastAPI, Query, Request, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(__file__))

# pastikan import ini bener
app = FastAPI()
app.include_router(transaction_controller.router)
