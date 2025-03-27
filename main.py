import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import yaml
import logging
from core.middleware.cors import setup_cors
from core.api.routes import auth, system, network, storage, logs, services, devices, settings
from modules.Fire.Simplex import Simplex
from modules.BMS.OmniMesh import COV
from modules.System.OmniWeb import Omniweb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

services_dict = {
    "OmniMesh": COV,
    "OmniWeb": Omniweb,
    "Simplex": Simplex
}

def load_config(file_path='config.yaml'):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Failed to load config from {file_path}: {e}")
        raise

def initialize_services(config):
    services_objects = {}
    
    for service in config.get('services', []):
        if service not in services_dict:
            logger.error(f"Service '{service}' not found in services_dict.")
            continue
        
        service_class = services_dict[service]
        try:
            services_objects[service] = service_class(config)
            if services_objects[service].start():
                logger.info(f"{service} Started Correctly")
            else:
                logger.warning(f"{service} Failed to Start")
        except Exception as e:
            logger.error(f"Error starting service {service}: {e}")
    
    return services_objects

app = FastAPI()

setup_cors(app)

app.include_router(auth.router, prefix="/api")
app.include_router(system.router, prefix="/api")
app.include_router(network.router, prefix="/api")
app.include_router(storage.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(settings.router, prefix="/api")

frontend_path = os.path.join(os.path.dirname(__file__), "/home/ubuntu/Omni-Net/frontend/build")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    file_path = os.path.join(frontend_path, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(frontend_path, "index.html"))

async def start_services():
    try:
        config = load_config('config.yaml')
        services_objects = initialize_services(config)
        return services_objects
    except Exception as e:
        logger.error(f"Service initialization failed: {e}")
        return {}

async def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, reload=True)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    services_task = asyncio.create_task(start_services())
    server_task = asyncio.create_task(run_server())
    await asyncio.gather(services_task, server_task)

if __name__ == "__main__":
    asyncio.run(main())