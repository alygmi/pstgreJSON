from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from models.models import Transaction
from main import app  
import pytest
import copy

client = TestClient(app)  

ts = 1745379156789
valid_payload = {
    "id": "1000000045-1745379123456",
    "ts": ts,
    "amount": 3.5,
    "status": "completed",
    "payment_method": "QRIS-MIDTRANS",
    "device_id": "bcd45f21-ef89-42d3-a7b2-67d890fa12bc",
    "device_tags": ["xyz123:ab", "cd:ef"],
    "dispense_code": 1,
    "payment_detail": {
        "detail": {
        "issuer": "SHOPEEPAY",
        "order_id": "1000000045-1745379123456",
        "transaction_id": "a1b2c3d4-5e6f-7890-1234-567890abcdef",
        "transaction_time": "2025-04-24 10:30:15"
        },
        "fee": {
        "mdr_qris": 0.015,
        "landlord_sharing_revenue": 0.42,
        "platform_sharing_revenue": 0.15
        },
        "nett": 2.925
    },
    "device_detail": {
        "device_name": "PH XYZ2"
    },
    "dispense_detail": {
        "dispense_status": "success",
        "dispense_ts": 1745387047856
    },
    "product_detail": {
        "name": "Spa Treatment",
        "sku": "SPA45",
        "price": 3.5
    },
    "refund_detail": {
        "refund_request_ts": None,
        "approval": None
    },
    "extras": {}
}

def test_database_state(db):
    """Verify the exact state of your test database"""
    # Check if table exists
    table_exists = db.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'transactions'
            AND table_schema = 'public'
        )
    """)).scalar()
    print(f"\nTable exists: {table_exists}")
    
    # Count records
    record_count = db.execute(text("SELECT COUNT(*) FROM transactions")).scalar()
    print(f"Records in table: {record_count}")
    
    # Show columns
    columns = db.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'transactions'
    """)).fetchall()
    print("\nTable columns:")
    for col in columns:
        print(f"- {col[0]}: {col[1]}")
    
    assert table_exists, "Transactions table missing in database"

@pytest.fixture
def test_insert_dummy():

    delete_transaction(ts)
    payload = copy.deepcopy(valid_payload)

    response = client.post("/transactions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

@pytest.fixture
def test_transaction(db):
    """Creates a test transaction with all required fields"""
    ts = int(time.time() * 1000)
    transaction = {
        "id": f"test-{ts}",
        "ts": ts,
        "status": "completed",
        "amount": 10.0,
        "payment_method": "QRIS-MIDTRANS",
        "device_id": "test-device",
        "device_tags": [],
        "dispense_code": 1,
        "payment_detail": {},
        "device_detail": {},
        "dispense_detail": {},
        "product_detail": {},
        "refund_detail": {},
        "extras": {}
    }
    db.execute(
        text("""
        INSERT INTO transactions 
        VALUES (
            :id, :ts, :status, :amount, :payment_method, 
            :device_id, :device_tags, :dispense_code, 
            :payment_detail, :device_detail, :dispense_detail,
            :product_detail, :refund_detail, :extras
        )
        """),
        transaction
    )
    db.commit()
    return transaction

def test_database_connection(db):
    # Check which database we're actually connected to
    db_name = db.execute(text("SELECT current_database()")).scalar()
    print(f"\nACTUAL DATABASE CONNECTED: {db_name}")
    assert db_name == "your_expected_db_name", "Connected to wrong database!"

def test_schema_search_path(db):
    # Check available schemas and search path
    schemas = db.execute(text("SELECT nspname FROM pg_namespace")).fetchall()
    search_path = db.execute(text("SHOW search_path")).scalar()
    print(f"\nSCHEMAS: {schemas}")
    print(f"SEARCH PATH: {search_path}")

def test_db_state(db):
    # List all transactions
    result = db.execute(text("SELECT * FROM transactions")).fetchall()
    print(f"Found {len(result)} transactions in test DB")
    assert len(result) > 0, "No transactions found - check your test setup"

def test_refund_transaction_success(client, dummy_transaction):
    ts = dummy_transaction.ts
    response = client.put(f"/transactions/refund/{ts}")
    assert response.status_code == 200

    data = response.json()
    refund_detail = data["refund_transaction"]["refund_detail"]

    assert refund_detail["approval"] is True
    assert isinstance(refund_detail["refund_request_ts"], int)


def test_refund_transaction_not_found():
    """
    Test untuk memastikan refund gagal ketika transaksi tidak ditemukan
    """
    fake_ts = 9999999999999  # TS yang tidak ada dalam database
    response = client.put(f"/transactions/refund/{fake_ts}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction Not found" or "Transaction not found"

def test_refund_transaction_already_refunded(db: Session):
    """
    Test untuk memastikan refund gagal jika transaksi sudah direfund sebelumnya
    """
    # Masukkan dummy transaction yang sudah direfund
    ts = 1750476615001
    transaction = Transaction(
        id="test_already_refunded",
        ts=ts,
        status="paid",
        amount=5000,
        payment_method="cash",
        device_id="dev-123",
        device_tags=["tag1"],
        dispense_code=1,
        payment_detail={"paid": True},
        device_detail={"model": "X"},
        dispense_detail={},
        product_detail={},
        refund_detail={
            "refund_request_ts": 1750476615001,
            "approval": True
        },
        extras={}
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Coba refund lagi
    response = client.put(f"/transactions/refund/{ts}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Transaction already refunded!"

    # Cleanup
    db.delete(transaction)
    db.commit()