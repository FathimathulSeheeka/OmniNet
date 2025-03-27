from fastapi import HTTPException
import yaml
import os

def view_config(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Configuration file not found.")
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file) or {}
            return config
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def edit_config(file_path, updates):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Configuration file not found.")
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file) or {}

        broadcast_type = updates.pop("broadcast_type", None)

        for key_path, new_value in updates.items():
            keys = key_path.split(".")  
            current = config
            for key in keys[:-1]: 
                if key not in current:
                    raise KeyError(f"Key '{key}' not found in configuration")
                current = current[key]

            last_key = keys[-1]
            if last_key in current:
                current[last_key] = new_value
            else:
                raise KeyError(f"Key '{last_key}' not found in configuration")
        if broadcast_type:
            if broadcast_type == "MQTT":
                config["services"]["Simplex"]["FACP0001"]["broadcast"] = {
                    "method": "MQTT",
                    "ip": "mqtts.sibcaconnect.com",
                    "port": 1883,
                    "username": "test",
                    "password": "test"
                }
            elif broadcast_type == "SNMP":
                config["services"]["Simplex"]["FACP0001"]["broadcast"] = {
                    "method": "SNMP",
                    "ip": "127.0.0.1",
                    "trap_ip": "127.0.0.1",
                    "port": 161,
                    "trap_port": 162,
                    "community": "public",
                    "panel_id": 1
                }
            else:
                raise ValueError("Invalid broadcast type. Choose 'MQTT' or 'SNMP'.")

        with open(file_path, "w") as file:
            yaml.dump(config, file, default_flow_style=False)

        return {"status": "success", "message": "Configuration updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))