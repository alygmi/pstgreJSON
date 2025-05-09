from pydantic import BaseModel, validator, Field
from decimal import Decimal
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class TransactionCreate(BaseModel):
    id: str
    ts: int  # Sesuai dengan BigInteger di SQLAlchemy
    status: str
    amount: Decimal
    payment_method: str
    device_id: str
    device_tags: Optional[List[str]] = Field(default_factory=list)
    dispense_code: Optional[Decimal] = Decimal('0')
    payment_detail: Optional[Dict[str, Any]] = Field(default_factory=dict)
    device_detail: Optional[Dict[str, Any]] = Field(default_factory=dict)
    dispense_detail: Optional[Dict[str, Any]] = Field(default_factory=dict)
    product_detail: Optional[Dict[str, Any]] = Field(default_factory=dict)
    refund_detail: Optional[Dict[str, Any]] = Field(default_factory=dict)
    extras: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('amount', 'dispense_code', pre=True)
    def convert_to_decimal(cls, v):
        if v is None:
            return Decimal('0')
        return Decimal(str(v))

    @validator('ts', pre=True)
    def convert_to_int(cls, v):
        return int(v)

    @validator('payment_detail', 'device_detail', 'dispense_detail',
               'product_detail', 'refund_detail', 'extras', pre=True)
    def parse_json_fields(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}


class TsRangeRequest(BaseModel):
    ts_start: Optional[int] = None
    ts_end: Optional[int] = None


class TransactionById(BaseModel):
    id: str


class TransactionByStatus(BaseModel):
    status: str


class TransactionByPayment(BaseModel):
    payment_method: str
