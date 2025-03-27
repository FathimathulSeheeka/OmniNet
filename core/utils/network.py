import re,os
import subprocess
import yaml
import time
from datetime import datetime, timedelta
from fastapi import HTTPException


BACKUP_FILE = "/home/ubuntu/backend/netplan.yaml"
CONFIG_FILE = "/etc/netplan/50-cloud-init.yaml"

def read_yaml_file():
    try:
        password = 'Sibca@1234!'
        result = subprocess.run(
            ["sudo", "-S", "cat", "/etc/netplan/50-cloud-init.yaml"], 
            input=password + '\n', capture_output=True, text=True, check=True
        )
        yaml_content = yaml.safe_load(result.stdout)
        return yaml_content
    except subprocess.CalledProcessError as e:
        return {"error": f"Error reading file: {e.stderr}"}
    except Exception as e:
        return {"error": str(e)}
    
def edit_netplan(config):
    main_file_path = CONFIG_FILE
    temp_file_path = BACKUP_FILE
    password = 'Sibca@1234!'
    try:
        result = subprocess.run(
            ["sudo", "-S", "cat", main_file_path], 
            input=password + '\n', capture_output=True, text=True, check=True
        )
        config_data = yaml.safe_load(result.stdout)

        keys = config.key.split(".")
        temp = config_data

        for subkey in keys[:-1]:
            if subkey not in temp or not isinstance(temp[subkey], dict):
                raise HTTPException(status_code=400, detail=f"Invalid path: {config.key}")
            temp = temp[subkey]

        temp[keys[-1]] = config.value  

        with open(temp_file_path, "w") as temp_file:
            yaml.dump(config_data, temp_file, default_flow_style=False)

        subprocess.run(["sudo", "mv", temp_file_path, main_file_path], check=True)

        subprocess.run(["sudo", "netplan", "apply"], check=True)

        return {"status": "success", "message": "Netplan configuration updated and applied successfully."}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Netplan configuration file not found.")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error applying netplan: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating netplan: {str(e)}")

def backup_config():
    if not os.path.exists(BACKUP_FILE):
        subprocess.run(["sudo", "cp", CONFIG_FILE, BACKUP_FILE], check=True)

def is_config_modified():
    if not os.path.exists(BACKUP_FILE):
        return {"status": "error", "message": "Configuration or backup file is missing."}

    try:
        result = subprocess.run(["sudo", "diff", CONFIG_FILE, BACKUP_FILE], capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "unchanged", "message": "No changes detected."}
        else:
            return {"status": "modified", "message": "Configuration has been modified."}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error checking config: {e.stderr}"}
    

def get_established_connections():
    try:
        command = ['sudo', '-S', 'lsof', '-i', '-P', '-n']
        password = 'Sibca@1234!'  
        result = subprocess.run(
            command,
            input=f'{password}\n',
            text=True,
            capture_output=True,
            check=True
        )
        established_connections = [
            line for line in result.stdout.splitlines()
            if 'ESTABLISHED' in line
        ]
        extracted = []
        for conn in established_connections:
           parts = conn.split()
           extracted.append(parts)
        return extracted
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return [e]

def get_ip_address():
    try:
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        return result.stdout.strip().split()
    except Exception as e:
        return {"error": str(e)}

def get_iccid():
    try:
        result = subprocess.run(["mmcli", "-i", "0"], capture_output=True, text=True)
        output = result.stdout

        for line in output.split("\n"):
            if "iccid" in line:
                return line.split(":")[-1].strip()

        return {"SIM not found"}
    except Exception as e:
        return {str(e)}
    
def get_signal_strength():
    try:
        result = subprocess.run(["mmcli", "-m", "0"], capture_output=True, text=True)
        output = result.stdout
        stderr = result.stderr
        if output:
            match = re.search(r"signal quality:\s+(\d+)%", output)
            if match:
                return f"{match.group(1)}%"
        elif stderr and "couldn't find modem" in stderr:
            print("[DEBUG] Modem not found. Restarting ModemManager...")
        else:
            raise HTTPException(status_code=500, detail="Unable to parse signal strength")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_modem_info():
    try:
        result = subprocess.run(["mmcli", "-m", "0"], capture_output=True, text=True)
        output = result.stdout

        imei, manufacturer, model, firmware = "Unknown", "Unknown", "Unknown", "Unknown"

        for line in output.split("\n"):
            if "imei" in line.lower():
                imei = line.split(":")[-1].strip()
            elif "manufacturer" in line.lower():
                manufacturer = line.split(":")[-1].strip()
            elif "model" in line.lower():
                model = line.split(":")[-1].strip()
            elif "revision" in line.lower():
                firmware = line.split(":")[-1].strip()

        return {
            "imei": imei,
            "manufacturer": manufacturer,
            "model": model,
            "firmware_version": firmware
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def get_tun0_speed():
    try:
        rx_bytes_1 = int(open("/sys/class/net/tun0/statistics/rx_bytes").read().strip())
        tx_bytes_1 = int(open("/sys/class/net/tun0/statistics/tx_bytes").read().strip())

        time.sleep(1)  

        rx_bytes_2 = int(open("/sys/class/net/tun0/statistics/rx_bytes").read().strip())
        tx_bytes_2 = int(open("/sys/class/net/tun0/statistics/tx_bytes").read().strip())

        rx_speed = (rx_bytes_2 - rx_bytes_1) / 1024  
        tx_speed = (tx_bytes_2 - tx_bytes_1) / 1024  

        return {"download_speed_kbps": round(rx_speed, 2), "upload_speed_kbps": round(tx_speed, 2)}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Interface 'tun0' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def get_data_usage(period: str = "monthly"):
    period_map = {
        "yearly": "-y",
        "monthly": "-m",
        "daily": "-d",
        "hourly": "-h"
    }
    if period not in period_map:
        raise ValueError("Invalid period. Choose from 'yearly', 'monthly', 'daily', or 'hourly'.")

    try:
        vnstat_output = subprocess.check_output(["vnstat", period_map[period]], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing vnstat: {e}")
        return None
    print(f"VNSTAT {period.capitalize()} Output:\n", vnstat_output)

    now = datetime.now()
    current_year = str(now.year)
    current_month = f"{now.year}-{now.month:02d}"
    current_day = f"{now.year}-{now.month:02d}-{now.day:02d}"
    current_hour = f"{now.hour:02d}"  

    regex_patterns = {
        "yearly": rf'({current_year})\s+[\d.]+\s+\w+\s+\|\s+[\d.]+\s+\w+\s+\|\s+([\d.]+\s+\w+)',
        "monthly": rf'({current_month})\s+[\d.]+\s+\w+\s+\|\s+[\d.]+\s+\w+\s+\|\s+([\d.]+\s+\w+)',
        "daily": rf'({current_day})\s+[\d.]+\s+\w+\s+\|\s+[\d.]+\s+\w+\s+\|\s+([\d.]+\s+\w+)',
        "hourly": rf'({current_hour}):\d{{2}}\s+\|\s+([\d.]+\s+\w+)'
    }

    pattern = re.compile(regex_patterns[period])
    matches = pattern.findall(vnstat_output)

    unit_multipliers = {'KiB': 1/1024, 'MiB': 1, 'GiB': 1024, "B": 1/(1024*1024)}
    usage_data = {}

    for timestamp, total in matches:
        value, unit = total.split()
        value = float(value)

        print(f"DEBUG: Timestamp={timestamp}, Value={value}, Unit={unit}")

        if unit not in unit_multipliers:
            print(f"ERROR: Unexpected unit '{unit}' found. Update unit_multipliers dictionary.")
            return None  
        usage_data[timestamp] = round(value * unit_multipliers[unit], 3)

    return usage_data
    

def get_vnstat_hourly_total_epoch():
    try:
        result = subprocess.run(["vnstat", "-h"], capture_output=True, text=True, check=True)
        output_lines = result.stdout.split("\n")
        hourly_data = {}

        current_date = None  

        for line in output_lines:
            date_match = re.match(r"\s*(\d{4}-\d{2}-\d{2})", line)
            if date_match:
                current_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
                continue 

            match = re.match(r"\s*(\d{2}):00\s+.*?\|\s+.*?\|\s+(\d+\.\d+\s+[KMG]iB)", line)
            if match and current_date:
                hour = int(match.group(1)) 
                total_usage = match.group(2)  

                entry_datetime = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour)
                epoch_time = int(time.mktime(entry_datetime.timetuple()))

                hourly_data[epoch_time] = total_usage  

        return hourly_data
    except subprocess.CalledProcessError as e:
        print("Error running vnstat:", e)
        return None


def get_vnstat_monthly():
    try:
        result = subprocess.run(["vnstat", "-m"], capture_output=True, text=True, check=True)
        output_lines = result.stdout.split("\n")
        monthly_data = {}

        for line in output_lines:
            match = re.match(r"\s*(\d{4}-\d{2})\s+.*?\|\s+.*?\|\s+(\d+\.\d+\s+[KMG]iB)\s+\|.*", line)
            if match:
                month = match.group(1)  
                total_usage = match.group(2)  

                monthly_data[month] = total_usage  

        return monthly_data  
    except subprocess.CalledProcessError as e:
        print("Error running vnstat:", e)
        return None

def get_vnstat_daily():
    try:

        result = subprocess.run(["vnstat", "-d"], capture_output=True, text=True, check=True)
        output_lines = result.stdout.split("\n")
        daily_data = {}

        for line in output_lines:
            match = re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+.*?\|\s+.*?\|\s+(\d+\.\d+\s+[KMG]iB)\s+\|.*", line)
            if match:
                date = match.group(1)  
                total_usage = match.group(2) 

                daily_data[date] = total_usage  

        return daily_data  
    except subprocess.CalledProcessError as e:
        print("Error running vnstat:", e)
        return None

def get_vnstat_usage():
    return [get_vnstat_hourly_total_epoch(), get_vnstat_daily(), get_vnstat_monthly()]