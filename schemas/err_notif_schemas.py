from pydantic import BaseModel

class NotificationInput(BaseModel):
    machineNo: str
    error: str
    noteError: str
    errorDate: str