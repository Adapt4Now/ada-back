from fastapi import APIRouter

router = APIRouter()


@router.get("/tasks/reports/summary")
async def get_task_summary():
    return {"message": "get_task_summary endpoint"}


@router.get("/tasks/reports/user/{user_id}")
async def get_user_task_report():
    return {"message": "get_user_task_report endpoint"}


@router.get("/tasks/reports/group/{group_id}")
async def get_group_task_report():
    return {"message": "get_group_task_report endpoint"}
