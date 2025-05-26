from sqlalchemy import BigInteger, Column, String, Numeric, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True) 
    ts = Column(BigInteger)
    status = Column(String)
    amount = Column(Numeric)
    payment_method = Column(String)
    device_id = Column(String)
    device_tags = Column(ARRAY(String), nullable=True)
    dispense_code = Column(Numeric)
    payment_detail = Column(JSON)
    device_detail = Column(JSON)
    dispense_detail = Column(JSON)
    product_detail = Column(JSON)
    refund_detail = Column(JSON)
    extras = Column(JSON, nullable=True)
