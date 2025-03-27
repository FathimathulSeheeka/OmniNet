import subprocess
from fastapi import HTTPException


def get_all_services_status():
    try:
        result = subprocess.run(["systemctl", "list-units", "--type=service", "--no-pager", "--all"], capture_output=True, text=True)
        services = []
        for line in result.stdout.split("\n"):
            parts = line.split()
            if len(parts) > 3:
                service_name = parts[0]
                status = parts[2]
                services.append({"service": service_name, "status": status})
        return services
    except Exception as e:
        return {"error": str(e)}    


def restart_service(service_name):    
    try:
        status_check = subprocess.run(["systemctl", "is-active", service_name], capture_output=True, text=True)
        if "inactive" in status_check.stdout or "failed" in status_check.stdout:
            return {"status": "warning", "message": f"Service '{service_name}' is not running."}
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        status_check = subprocess.run(["systemctl", "is-active", service_name], capture_output=True, text=True)
        if "active" in status_check.stdout:
            return {"status": "success", "message": f"Service '{service_name}' restarted successfully"}
        else:
            return {"status": "error", "message": f"Failed to restart service '{service_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def stop_service(service_name):
    try:
        result = subprocess.run(
            ["sudo","systemctl", "stop", service_name],
            check=True,
            capture_output=True,
            text=True
        )
        return f"Service '{service_name}' stopped successfully."
    except subprocess.CalledProcessError as e:
        return f"Failed to stop service '{service_name}': {e.stderr}"


def start_service(service_name):
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "start", service_name],
            check=True,
            capture_output=True,
            text=True
        )
        return f"Service '{service_name}' started successfully."
    except subprocess.CalledProcessError as e:
        return f"Failed to start service '{service_name}': {e.stderr}"
    
def disable_service(service_name):
    try:
        result = subprocess.run(
            ["sudo","systemctl", "disable", service_name],
            check=True,
            capture_output=True,
            text=True
        )
        return f"Service '{service_name}' disabled successfully."
    except subprocess.CalledProcessError as e:
        return f"Failed to disable service '{service_name}': {e.stderr}"


def get_version():
    from main import services_dict
    versions = {}

    for service in services_dict:
        versions[service] = services_dict[service].version
    return versions
