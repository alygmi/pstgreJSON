from main import app
from fastapi.testclient import TestClient
import pytest
import copy

client = TestClient(app)

def test_searchby_status():
    payload = {
        "payment_method": "QRIS-DUMMY"
    }
    response = client.post("/transactions/bypayment", json=payload)
    assert response.status_code == 200

def test_search_byid_no_valid_data():
    payload = {
        "payment_method": "closed"
    }
    response = client.post("/transactions/bypayment", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_search_missing_payment_field():
    payload = {}
    response = client.post("/transactions/bypayment", json=payload)
    assert response.status_code == 422

def test_search_payment_empty():
    payload = {"payment_method" : ""}
    response = client.post("/transactions/bypayment", json=payload)
    assert response.status_code == 422

def test_search_by_payment_invalid_data():
    payload = {
        "payment_method": 1234567 
    }
    response = client.post("/transactions/bypayment", json=payload)
    assert response.status_code == 422