from fastapi import APIRouter, Depends
from core.api.dependencies import get_current_user
from core.models.schemas import TokenData
from core.utils.devices import *

router = APIRouter()

@router.get("/devices")
async def get_devices_api(current_user: TokenData = Depends(get_current_user)):
    return get_devices()