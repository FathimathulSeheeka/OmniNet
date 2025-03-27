import time
import subprocess
import os
import signal
import psutil
from fastapi import HTTPException

def get_top_cpu_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:20]


def kill_process(pid: int):
    try:
        if not psutil.pid_exists(pid):
            raise HTTPException(status_code=404, detail=f"Process with PID {pid} not found")

        try:
            os.kill(pid, signal.SIGKILL)
        except PermissionError:
            process = subprocess.Popen(
                ["sudo", "-S", "kill", "-9", str(pid)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            sudo_password = 'Sibca@1234!'
            stdout, stderr = process.communicate(input=f"{sudo_password}\n")

            if process.returncode != 0:
                raise HTTPException(status_code=500, detail=f"Failed to kill process {pid} with sudo: {stderr.strip()}")

        return {"message": f"Process {pid} has been killed successfully"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error killing process: {str(e)}")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied. Try running as root.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    return f"{uptime_hours}h {uptime_minutes}m"


def get_serial_number():
    try:
        with open("/proc/cpuinfo", "r") as file:
            for line in file:
                if line.startswith("Serial"):
                    return line.strip().split(":")[1].strip()
    except Exception as e:
        print(f"Error retrieving serial number: {e}")
    return "Unknown"

def get_gateway_time():
    try:
        system_time = subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"], text=True).strip()
        return system_time

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system time: {e}")
    

def update_gateway_time(timestamp:str = None):
    sudo_password = 'Sibca@1234!'
    try:
        if not timestamp:
            timestamp = get_gateway_time()
        
        cmd = ["sudo", "-S", "date", "-s", timestamp]

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=f"{sudo_password}\n" if sudo_password else "")
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error updating system time: {stderr.strip()}")
        system_time = subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"], text=True).strip()
        return {"status": "success", "system_time": system_time}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error updating system time: {e.stderr.strip()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def reboot_system():
    try:
        subprocess.run(["sudo", "reboot"], check=True)
        return None
    except Exception as e:
        return {"error": str(e)}
    

def update_system():
    return {"status": "update success"}