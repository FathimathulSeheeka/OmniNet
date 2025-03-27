import os
import subprocess

def get_devices(): 
    devices = []
    try:
        output = subprocess.check_output(["ls", "-l", "/dev/serial/by-id"], text=True).strip().split("\n")
        for line in output[1:]:  
            parts = line.split()
            if len(parts) >= 11:  
                device_id = os.path.basename(parts[-3])
                port = parts[-1].split("/")[-1]     
                devices.append({"id": device_id, "port": port})

        return {"devices": devices}
    except subprocess.CalledProcessError:
        return {"error": "No devices found or /dev/serial/by-id does not exist."}
    except Exception as e:
        return {"error": str(e)}