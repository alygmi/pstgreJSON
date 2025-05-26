from main import app
from fastapi.testclient import TestClient
import pytest
import copy

client = TestClient(app)

def test_searchby_status():
    payload = {
        "status": "settlement"
    }
    response = client.post("/transactions/bystatus", json=payload)
    assert response.status_code == 200

def test_search_byid_no_valid_data():
    payload = {
        "status": "closed"
    }
    response = client.post("/transactions/bystatus", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_search_missing_id_field():
    payload = {}
    response = client.post("/transactions/bystatus", json=payload)
    assert response.status_code == 422

def test_search_id_empty():
    payload = {"status" : ""}
    response = client.post("/transactions/bystatus", json=payload)
    assert response.status_code == 422

def test_search_byid_invalid_data():
    payload = {
        "status": 1234567 
    }
    response = client.post("/transactions/bystatus", json=payload)
    assert response.status_code == 422