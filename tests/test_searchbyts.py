from main import app
from fastapi.testclient import TestClient
import pytest
import copy

client = TestClient(app)
# def dummy_payload():
#     payload
def test_searchby_ts():
    payload = {
        "ts_start": 1750422610000,
        "ts_end": 1750423610000
    }
    response = client.post("/transactions/bytsrange", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    found = any(
        (tx.get("ts"))
        for tx in data
    )

    assert found

def test_search_bytsrange_not_valid_data():
    payload = {
        "ts_start": 1234567,
        "ts_end": 9082387 
    }
    response = client.post("/transactions/bytsrange", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_search_missing_ts_field():
    payload = {}
    response = client.post("/transactions/bytsrange", json=payload)
    assert response.status_code == 422

def test_search_ts_empty():
    payload = {"ts_start": ""}
    response = client.post("/transactions/bytsrange", json=payload)
    assert response.status_code == 422

def test_search_bytsrange_invalid_data():
    payload = {
        "ts_start": "109237891",
        "ts_end": "0912839874" 
    }
    response = client.post("/transactions/bytsrange", json=payload)
    assert response.status_code == 422
