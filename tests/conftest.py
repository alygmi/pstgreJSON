import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from main import app  # sesuaikan dengan nama file FastAPI kamu
from database import Base, get_db  # Base = declarative_base(), get_db = dependency
from models.models import Transaction  # Model transaksi kamu

# URL database untuk testing (gunakan test DB terpisah!)
SQLALCHEMY_DATABASE_URL = DATABASE_URL = "postgresql://postgres:password@m2mdev.tritronik.com:46433/smartvending"

# Setup engine & session
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_transaction(db):
    """Creates a test transaction that definitely exists"""
    ts = int(time.time() * 1000)  # Fresh timestamp
    trans = Transaction(
        id=f"test-{ts}",
        ts=ts,
        status="completed",
        refund_detail={}
    )
    db.add(trans)
    db.commit()
    return trans  # Return the created transaction

@pytest.fixture
def dummy_transaction(db):
    ts = 1750476615000  # ganti sesuai kebutuhan
    transaction = Transaction(
        id="dummy-abc",
        ts=ts,
        status="paid",
        amount=10000,
        payment_method="cash",
        device_id="device123",
        device_tags=["tag1", "tag2"],
        dispense_code=1,
        payment_detail={"method": "cash", "paid_at": ts},
        device_detail={"model": "X100", "vendor": "VendorX"},
        dispense_detail={"success": True},
        product_detail={"name": "Coke", "price": 10000},
        refund_detail=None,
        extras={}
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    yield transaction
    db.delete(transaction)
    db.commit()



@pytest.fixture(scope="session", autouse=True)
def verify_table_structure():
    """Ensure the table matches your model exactly"""
    with engine.connect() as conn:
        # Temporary raw SQL to verify
        try:
            result = conn.execute("SELECT id, ts FROM transactions LIMIT 1")
            print("\nTable verification succeeded")
        except Exception as e:
            print(f"\nTABLE VERIFICATION FAILED: {str(e)}")
            # Create table if missing
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id VARCHAR PRIMARY KEY,
                    ts BIGINT NOT NULL,
                    status VARCHAR,
                    amount FLOAT,
                    payment_method VARCHAR,
                    device_id VARCHAR,
                    device_tags TEXT[],
                    dispense_code INTEGER,
                    payment_detail JSONB,
                    device_detail JSONB,
                    dispense_detail JSONB,
                    product_detail JSONB,
                    refund_detail JSONB DEFAULT '{}'::JSONB,
                    extras JSONB
                )
            """))
            conn.commit()

@pytest.fixture
def ts():
    """Returns a unique timestamp for each test"""
    return int(time.time() * 1000)  # Current time in milliseconds

# Ganti dependency get_db agar pakai test session
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override dependency di app
app.dependency_overrides[get_db] = override_get_db

# Fixture utama untuk TestClient
@pytest.fixture(scope="module")
def client():
    # Buat tabel-tabelnya (jika belum)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c

    # Hapus semua setelah selesai (opsional)
    Base.metadata.drop_all(bind=engine)


# Fixture untuk akses session langsung
@pytest.fixture()
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Fixture untuk hapus 1 transaksi berdasarkan transaction_id
@pytest.fixture
def delete_transaction():
    def _delete(ts: int):
        db = TestingSessionLocal()
        try:
            db.query(Transaction).filter(Transaction.ts == ts).delete()
            db.commit()
        finally:
            db.close()
    return _delete