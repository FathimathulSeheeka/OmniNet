import psutil
import subprocess

def get_disk_usage():
        disk_usage = psutil.disk_usage("/")
        return round(disk_usage.used / (1024**3), 2), round(disk_usage.free / (1024**3), 2)

def get_memory_info():
    mem = psutil.virtual_memory()
    return {
        "used_memory": f"{mem.used / (1024 ** 2):.2f} MB",
        "total_memory": f"{mem.total / (1024 ** 2):.2f} MB"
    }

def get_largest_files_and_folders(path=".", count=10):
    try:
        result = subprocess.run(
            f"du -h --max-depth=10 {path} | sort -h -r", 
            capture_output=True, text=True, shell=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        items = []
        for line in lines:
            parts = line.split("\t")
            if len(parts) == 2:
                size, name = parts
                items.append({"size": size, "name": name})

        return items[:count]
    except subprocess.CalledProcessError as e:
        return {"error": str(e)}

