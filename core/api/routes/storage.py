from fastapi import APIRouter, Depends
from core.api.dependencies import get_current_user
from core.models.schemas import TokenData
from core.utils.storage import *

router = APIRouter()


@router.get("/storage")
async def storage_usage_api(current_user: TokenData = Depends(get_current_user)):
    return get_largest_files_and_folders()

@router.get("/memory")
async def get_memory_info_api(current_user: TokenData = Depends(get_current_user)):
    mem = get_memory_info()
    return mem

@router.get("/disk-usage")
async def get_disc_usage_api(current_user: TokenData = Depends(get_current_user)):
    usage = get_disk_usage()  
    return {"Usage": usage}

@router.get("/cpu-usage")
async def get_cpu_usage(current_user: TokenData = Depends(get_current_user)):
    return {"cpu_usage": f"{psutil.cpu_percent()}%"}