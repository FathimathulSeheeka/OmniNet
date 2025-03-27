import hashlib
import time
import os

def generate_otp(gateway_serial: str, time_window: int = 900):

    otps = {}

    USER_LEVELS = {
    "L1": os.getenv("USER_L1", "001"),  
    "L2": os.getenv("USER_L2", "002"),  
    "L3": os.getenv("USER_L3", "003"), 
    }

    timestamp = int(time.time() // time_window)
    for i in USER_LEVELS:
        data = f"{gateway_serial}{USER_LEVELS[i]}{timestamp}"
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        otp = str(int(hash_value, 16))[-6:]
        otps[i] = otp
    
    return otps