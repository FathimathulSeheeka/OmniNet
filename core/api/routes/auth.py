from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from core.config.config import ACCESS_TOKEN_EXPIRE_MINUTES
from core.config.security import create_access_token, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core.models.schemas import Token
from core.utils.security import generate_otp
from core.utils.system_info import get_serial_number

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


@router.get("/generate-otp")
async def get_otp():
    return {"otp": generate_otp(get_serial_number())}

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    gateway_role = form_data.username
    if gateway_role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": gateway_role}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
