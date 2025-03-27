from fastapi import APIRouter, Depends
from core.api.dependencies import get_current_user
from core.utils.settings import *
from core.models.schemas import TokenData

router = APIRouter()


CONFIG_FILE = "config.yaml" 

@router.get("/view-config")
def view_config_api(current_user: TokenData = Depends(get_current_user)):
    return view_config(CONFIG_FILE)


@router.post("/update-config")
def update_config(data: dict, current_user: TokenData = Depends(get_current_user)):
    if not data:
        raise HTTPException(status_code=400, detail="No updates provided.")
    return edit_config(CONFIG_FILE, data)