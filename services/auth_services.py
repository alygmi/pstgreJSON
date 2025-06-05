from repository.auth_repo import generate_token

def generate_dummy_token() -> dict:
    payload = {"id": "1", "user": "mosfeed"}
    token = generate_token(payload)
    return {"auth": True, "token": token}