from pydantic import BaseModel, validator, Field
from decimal import Decimal
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class TransactionCreate(BaseModel):
    id: str
    ts: int
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


class DeviceDetail(BaseModel):
    device_name: Optional[str] = None


class DispenseDetail(BaseModel):
    dispense_status: Optional[str] = None
    dispense_ts: Optional[int] = None  # diasumsikan timestamp dalam ms


class ProductDetail(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[int] = None


class RefundDetail(BaseModel):
    refund_request_ts: Optional[int] = None
    approval: Optional[bool] = None


class Extras(BaseModel):
    campaign: Optional[str] = None
    voucher_used: Optional[bool] = None


class PaymentFee(BaseModel):
    mdr_qris: Optional[float] = None
    landlord_sharing_revenue: Optional[float] = None
    platform_sharing_revenue: Optional[float] = None


class PaymentDetailDetail(BaseModel):
    issuer: Optional[str] = None
    order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    transaction_time: Optional[str] = None


class PaymentDetail(BaseModel):
    detail: Optional[PaymentDetailDetail] = None
    fee: Optional[PaymentFee] = None
    nett: Optional[float] = None


class TransactionUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[int] = None
    payment_method: Optional[str] = None
    device_id: Optional[str] = None
    device_tags: Optional[str] = None
    dispense_code: Optional[int] = None
    payment_detail: Optional[PaymentDetail] = None
    device_detail: Optional[DeviceDetail] = None
    dispense_detail: Optional[DispenseDetail] = None
    product_detail: Optional[ProductDetail] = None
    refund_detail: Optional[RefundDetail] = None
    extras: Optional[Extras] = None


class TsRangeRequest(BaseModel):
    ts_start: Optional[int] = None
    ts_end: Optional[int] = None


class TransactionById(BaseModel):
    id: str


class TransactionByStatus(BaseModel):
    status: str


class TransactionByPayment(BaseModel):
    payment_method: str
