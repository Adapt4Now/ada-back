from fastapi import APIRouter

router = APIRouter()


@router.get("/users/notifications")
async def get_notifications():
    return {"message": "get_notifications endpoint"}


@router.post("/users/notifications/read/{notification_id}")
async def mark_notification_as_read():
    return {"message": "mark_notification_as_read endpoint"}


@router.delete("/users/notifications/{notification_id}")
async def delete_notification():
    return {"message": "delete_notification endpoint"}
