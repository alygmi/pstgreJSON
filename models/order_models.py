from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base  # asumsi kamu sudah punya Base dari declarative_base()

class TransactionOrder(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String, nullable=False)
    transaction_id = Column(String, nullable=False)  # <- perbaikan dari 'transcation_id'
    date = Column(DateTime, nullable=False)
    machine_no = Column(String, nullable=False)
    machine_name = Column(String, nullable=False)
    location_id = Column(String, nullable=False)
    location_name = Column(String, default="")
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    recorded_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    mid = Column(String, default="")
    status = Column(Integer, nullable=False)
