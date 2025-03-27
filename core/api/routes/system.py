from fastapi import APIRouter, Depends
from core.api.dependencies import get_current_user
from core.utils.system_info import *
from core.models.schemas import TokenData

router = APIRouter()

@router.get("/system-info")
async def get_serial_number_api(current_user: TokenData = Depends(get_current_user)):
    return {
        "serial_no": get_serial_number(),
        "system_time": get_gateway_time()
    }


@router.post("/update-time")
async def update_time(timestamp: str = None, current_user: TokenData = Depends(get_current_user)):
    try:
        result = update_gateway_time(timestamp)
        return result
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Error updating system time: {e}")


@router.get("/top-processes")
async def get_top_running_process_api(current_user: TokenData = Depends(get_current_user)):
    return get_top_cpu_processes()

@router.delete("/action/{processId}")
async def kill_running_process(processId:int, current_user: TokenData = Depends(get_current_user)):
    return kill_process(processId)

@router.get("/uptime")
async def get_uptime_api(current_user: TokenData = Depends(get_current_user)):
    return {"Uptime": get_uptime()}

@router.post("/reboot")
async def reboot(current_user: TokenData = Depends(get_current_user)):
    return reboot_system()


@router.post("/update-system")
async def update_system_api(current_user: TokenData = Depends(get_current_user)):
    return update_system()