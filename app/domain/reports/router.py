from typing import List

from fastapi import APIRouter, Depends

from app.domain.tasks.schemas import TaskResponseSchema
from app.domain.reports.service import ReportService
from app.dependencies import get_report_service

router = APIRouter()


@router.get("/tasks/reports/summary")
async def get_task_summary(
    service: ReportService = Depends(get_report_service),
):
    return await service.get_task_summary()


@router.get("/tasks/reports/user/{user_id}", response_model=List[TaskResponseSchema])
async def get_user_task_report(
    user_id: int, service: ReportService = Depends(get_report_service)
):
    return await service.get_user_task_report(user_id)


@router.get("/tasks/reports/assigned-by/{user_id}", response_model=List[TaskResponseSchema])
async def get_tasks_assigned_by_user(
    user_id: int, service: ReportService = Depends(get_report_service)
):
    return await service.get_tasks_assigned_by_user(user_id)


@router.get("/tasks/reports/group/{group_id}", response_model=List[TaskResponseSchema])
async def get_group_task_report(
    group_id: int, service: ReportService = Depends(get_report_service)
):
    return await service.get_group_task_report(group_id)


@router.get("/tasks/reports/user/{user_id}/groups", response_model=List[TaskResponseSchema])
async def get_user_groups_tasks(
    user_id: int, service: ReportService = Depends(get_report_service)
):
    return await service.get_user_groups_tasks(user_id)
