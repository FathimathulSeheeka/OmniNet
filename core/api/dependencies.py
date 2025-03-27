import jwt
from fastapi import Depends, HTTPException, status
from core.config.config import SECRET_KEY, ALGORITHM
from core.api.routes.auth import oauth2_scheme

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")   
        role = payload.get("role")

        if username is None or role is None:
            return {"username": username, "role": role}

        return {"username": username, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise credentials_exception