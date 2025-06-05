from fastapi import APIRouter
from services.auth_services import generate_dummy_token

router = APIRouter()

@router.get("/transactions/jwtlogin")
def get_dummy_token():
    return generate_dummy_token()