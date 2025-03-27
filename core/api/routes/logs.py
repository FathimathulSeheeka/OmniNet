from fastapi import APIRouter, Depends
from core.api.dependencies import get_current_user
from core.models.schemas import TokenData
from core.utils.logs import *

router = APIRouter()

@router.get("/log-files")
async def list_log_files_api(current_user: TokenData = Depends(get_current_user)):
    return list_log_files()

@router.get("/date-created")
async def list_log_folders_api(current_user: TokenData = Depends(get_current_user)):
    return list_log_folders()

@router.get("/log")
async def get_log_api(file_name: str, current_user: TokenData = Depends(get_current_user)):
    return get_log(file_name)

@router.delete("/delete-log")
async def delete_log_api(file_name:str, current_user: TokenData = Depends(get_current_user)):
    return delete_log(file_name)

@router.get("/download-log")
async def download_log_api(file_name:str, current_user: TokenData = Depends(get_current_user)):
    return download_log(file_name)