from controller import transaction_controller
from fastapi import FastAPI

# pastikan import ini bener
app = FastAPI()
app.include_router(transaction_controller.router)
