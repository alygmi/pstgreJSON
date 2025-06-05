from repository.err_notif_repo import send_notification_to_target

def process_notification(data: dict) -> dict:
    result = send_notification_to_target(data)
    return {
        "status": "SUCCESS",
        "message": "Send Notification Success",
        "statusNotifikasi": result
    }