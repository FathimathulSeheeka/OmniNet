from pydantic import BaseModel
from typing import Optional, Any

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    gateway_serial: Optional[str] = None

class NetplanUpdate(BaseModel):
    key: str 
    value: Any

class LogDelete(BaseModel):
    file_name: str