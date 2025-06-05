from fastapi import APIRouter
from pydantic import BaseModel
from schemas.err_notif_schemas import NotificationInput
from services.err_notif_services import process_notification

router = APIRouter()

# class NotificationInput(BaseModel):
#     machineNo: str
#     error: str
#     noteError: str
#     errorDate: str  # Jika ingin bisa divalidasi otomatis: datetime

@router.post("/transactions/notiferr")
def send_notification(payload: NotificationInput):
    return process_notification(payload.dict())