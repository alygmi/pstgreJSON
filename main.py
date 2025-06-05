from controller import transaction_controller, err_notif_controller
from controller.auth_controller import router as token_router
from fastapi import FastAPI

# pastikan import ini bener
app = FastAPI()
app.include_router(transaction_controller.router)
app.include_router(token_router)
app.include_router(err_notif_controller.router)