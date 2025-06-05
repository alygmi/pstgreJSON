from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class TransactionCreateOrder(BaseModel):
    order_no: str
    transaction_id: str
    date: datetime
    machine_no: str
    machine_name: str
    location_id: str
    location_name: Optional[str] = ""
    product_id: str
    product_name: str
    recorded_price: float
    quantity: int
    mid: Optional[str] = ""
    status: int

    class Config:
        orm_mode = True


class TransactionResponse(TransactionCreateOrder):
    id: str
