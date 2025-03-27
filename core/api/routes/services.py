from fastapi import APIRouter, Depends
from core.api.dependencies import get_current_user
from core.models.schemas import TokenData
from core.utils.services import *
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/service-status")
async def get_service_status_api(current_user: TokenData = Depends(get_current_user)):
    return get_all_services_status()

@router.post("/restart-service")
async def restart_service_api(service_name: str, current_user: TokenData = Depends(get_current_user)):
    return restart_service(service_name)

@router.post("/start-service")
async def start_service_api(service_name: str, current_user: TokenData = Depends(get_current_user)):
    return start_service(service_name)

@router.post("/stop-service")
async def stop_service_api(service_name: str, current_user: TokenData = Depends(get_current_user)):
    return stop_service(service_name)


@router.post("/disable-service")
async def disable_service_api(service_name: str, current_user: TokenData = Depends(get_current_user)):
    return disable_service(service_name)


@router.get("/journal")
async def get_journal(service_name: str = "fastapi", lines: int = 10, current_user: TokenData = Depends(get_current_user)):
    try:
        cmd = ["journalctl", "-u", service_name, "--lines", str(lines)]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def iter_lines():
            for line in iter(process.stdout.readline, ""):
                yield line
            process.stdout.close()

            process.wait()
            stderr = process.stderr.read().strip()
            if stderr:
                raise HTTPException(status_code=500, detail=f"Error fetching logs: {stderr}")

        return StreamingResponse(iter_lines(), media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.get("/version")
async def get_version_api():
    return get_version()