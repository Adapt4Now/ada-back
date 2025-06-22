from fastapi import APIRouter

router = APIRouter()


@router.get("/settings")
async def get_settings():
    return {"message": "get_settings endpoint"}


@router.put("/settings")
async def update_settings():
    return {"message": "update_settings endpoint"}
