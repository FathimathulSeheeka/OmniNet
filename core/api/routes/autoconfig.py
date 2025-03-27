from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from core.api.dependencies import get_current_user
from core.models.schemas import TokenData
import subprocess
import shutil
import os

router = APIRouter()

VPN_CONFIG_PATH = "/etc/openvpn/client.conf"  
VPN_CONFIG_DIR = "/etc/openvpn/" 

@router.post("/setup-vpn")
def setup_vpn(file: UploadFile = File(...), current_user: TokenData = Depends(get_current_user)):
    try:

        if not os.path.exists(VPN_CONFIG_DIR):
            os.makedirs(VPN_CONFIG_DIR, exist_ok=True)

        destination_path = os.path.join(VPN_CONFIG_DIR, file.filename)

        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        for filename in os.listdir(VPN_CONFIG_DIR):
            if filename.endswith(".ovpn"):
                file_path = os.path.join(VPN_CONFIG_DIR, filename)
                os.remove(file_path)
        
        subprocess.run(["sudo", "openvpn", "--client", "--config", VPN_CONFIG_PATH], check=True)

        subprocess.run(["sudo", "systemctl", "restart", "openvpn@client"], check=True)

        vpn_ip = subprocess.check_output(["ip", "a"]).decode()

        return {
            "status": "VPN setup complete",
            "file_saved": destination_path,
            "vpn_ip": vpn_ip
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))