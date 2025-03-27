from fastapi import APIRouter, Depends
from core.api.dependencies import get_current_user
from core.utils.system_info import *
from core.models.schemas import TokenData, NetplanUpdate
from core.utils.network import *
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/netplan")
async def view_netplan(current_user: TokenData = Depends(get_current_user)):
    yaml_data = read_yaml_file()
    return JSONResponse(content=yaml_data)


@router.post("/apply-netplan")
async def edit_netplan_api(config: NetplanUpdate, current_user: TokenData = Depends(get_current_user)):
    return edit_netplan(config)

@router.get("/active-network")
async def active_connections(current_user: TokenData = Depends(get_current_user)):
    return get_established_connections()

@router.get("/modem-info")
async def get_modem_info_endpoint(current_user: TokenData = Depends(get_current_user)):
    return get_modem_info()

@router.get("/network-info")
async def get_network_info_api(current_user: TokenData = Depends(get_current_user)):
    if len(get_ip_address()) == 3:
        return {"wwan0": get_ip_address()[0], "wlan0": get_ip_address()[1], "gateway": get_ip_address()[2], "SIM": get_iccid(), "signal strength" : get_signal_strength()}
    return {"wwan0": "192.168.100.48", "wlan0": get_ip_address()[0], "gateway": get_ip_address()[1], "SIM": get_iccid(), "signal strength" : get_signal_strength()}
    

@router.get("/tun0-speed")
async def network_speed(current_user: TokenData = Depends(get_current_user)):
    return get_tun0_speed()

@router.get("/data-usage")
async def get_data_usage_api(period:str, current_user: TokenData = Depends(get_current_user)):
    usage = get_data_usage(period)  
    return f'{"Usage"}: {usage} MiB'

@router.get("/vnstat-graph")
async def get_vnstat_api(current_user: TokenData = Depends(get_current_user)):
    return get_vnstat_usage()

@router.get("/modules")
async def get_module_info_api(current_user: TokenData = Depends(get_current_user)):
    return {"Simplex":"0.3.2", "OmniNet": "0.3.2", "Omni-Mesh":"0.3.2"}