from fastapi.testclient import TestClient
from main import app  
import pytest
import copy
# import conftest

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

@pytest.fixture
def test_insert_transaction():

    delete_transaction(ts)
    payload = copy.deepcopy(valid_payload)

    response = client.post("/transactions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

@pytest.fixture
def test_insert_missing_required_field():
    ts = 1745379156789

    delete_transaction(ts)
    payload["detail"][0]["price"] = -10000
    response = client.post("/transactions", json=invalid_payload)
    assert response.status_code == 422  # kasih keluaran tersebut jika benar

    error_response = response.json()
    assert "detail" in error_response

    # Cek kalau 'amount' termasuk dalam pesan error
    # error_fields = [err["loc"][-1] for err in error_response["detail"]]
    # assert "amount" in error_fields

@pytest.fixture
def test_insert_invalid_data_type():
    ts = 1745379156789

    delete_transaction(ts)
    payload = copy.deepcopy(valid_payload)
    payload["amount"] = "satu"  # seharusnya int
    response = client.post("/transactions", json=payload)
    assert response.status_code == 422

@pytest.fixture
def test_insert_empty_data():
    ts = 1745379156789

    delete_transaction(ts)
    response = client.post("/transactions", json={})
    assert response.status_code == 422

@pytest.fixture
def test_insert_negative_data():
    ts = 1745379156789

    delete_transaction(ts)
    response = client.post("/transactions", json=invalid_payload)
    assert response.status_code == 422
    assert "greater_than" in response.text


def test_insert_data_duplicate():
    payload = {
        "id": "1000000045-1745379123456",
        "ts": 1745379156789,
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
            "refund_ts": None
        },
        "extras": {}
    }
    response = client.post("/transactions", json=payload)
    assert response.status_code == 400
    assert "duplicate" in response.text.lower()

@pytest.fixture
def test_insert_invalid_timestamp():
    ts = 1745379156789

    delete_transaction(ts)
    payload = copy.deepcopy(valid_payload)
    payload["payment_time"] = "not-a-date"
    response = client.post("/transactions", json=payload)
    assert response.status_code == 422

def test_insert_malformed_json():
    bad_json = '{"amount": 1, "application_id": "1000000044", '  # JSON belum selesai
    response = client.post(
        "/transactions",
        data=bad_json,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400

@pytest.fixture
def test_insert_invalid_enum():
    ts = 1745379156789

    delete_transaction(ts)
    payload = copy.deepcopy(valid_payload)
    payload["payment_method"] = "BITCOIN"  # anggap enum-nya gak ada BITCOIN
    response = client.post("/transactions", json=payload)
    assert response.status_code == 422

    

# untuk pengetestan pagination
def test_get_transactions_success():
    response = client.get("/transactions/get?limit=5&offset=0")
    assert response.status_code == 200