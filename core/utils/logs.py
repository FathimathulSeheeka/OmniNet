import os
from fastapi import HTTPException
from fastapi.responses import FileResponse


log_dir = "/opt/omniconn-mesh/data/log/"


def list_log_files():
    try:
        files = os.listdir(log_dir)
        return {"log_files": files}
    except Exception as e:
        return {"error": str(e)}
    
def list_log_folders():
    try:
        entries = os.listdir(log_dir)
        folders = {log_dir+entry : entry.split(".")[0] for entry in entries if os.path.isdir(os.path.join(log_dir, entry))}
        return folders
    except Exception as e:
        return {"error": str(e)}


def get_log(file_name):
    log_path = os.path.join(log_dir, file_name)
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    try:
        with open(log_path, "r") as log_file:
            return {"log_file": file_name, "content": log_file.readlines()}
    except Exception as e:
        return {"error": str(e)}
    
def delete_log(file_name:str):
    log_path = os.path.join(log_dir, file_name)
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    try:
        os.remove(log_path)
        return {"status": "success", "message": f"Log file '{file_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def download_log(file_name: str):
    log_path = os.path.join(log_dir, file_name)
    print(f"Requested file path: {log_path}")

    if not os.path.isfile(log_path):
        print(f"ERROR: File not found at {log_path}")
        raise HTTPException(status_code=404, detail="Log file not found")

    try:
        return FileResponse(
            log_path,
            filename=os.path.basename(log_path), 
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(log_path)}"}
        )
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {e}")