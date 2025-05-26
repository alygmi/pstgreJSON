from main import app
from fastapi.testclient import TestClient
import pytest
import copy

client = TestClient(app)

def test_searchby_id():
    payload = {
        "id": "1000000000-1740000000001"
    }
    response = client.post("/transactions/byid", json=payload)
    assert response.status_code == 200

def test_search_byid_no_valid_data():
    payload = {
        "id": "1000000000-1740000000231"
    }
    response = client.post("/transactions/byid", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_search_missing_id_field():
    payload = {}
    response = client.post("/transactions/byid", json=payload)
    assert response.status_code == 422

def test_search_id_empty():
    payload = {"id" }
    response = client.post("/transactions/byid", json=payload)
    assert response.status_code == 422

def test_search_byid_invalid_data():
    payload = {
        "id": 1234567 
    }
    response = client.post("/transactions/bytsrange", json=payload)
    assert response.status_code == 422