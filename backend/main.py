"""
Vylos - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import docker
from docker import errors as docker_errors
import threading

from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db import models
from app.api.v1.api import api_router
from app.middleware.cors import setup_cors
from app.utils.logging import setup_logging
from app.utils.exceptions import setup_exception_handlers


# Setup logging
logger = setup_logging()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Web Application Deployment Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup middleware
setup_cors(app)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)


def restore_nextjs_containers():
    """Start existing stopped Next.js containers - NO automatic rebuilds"""
    print("=" * 50)
    print("STARTING CONTAINER RESTORATION")
    print("=" * 50)
    
    try:
        client = docker.from_env()
        
        # Get all existing nextjs containers (running or stopped)
        containers = client.containers.list(all=True, filters={"name": "nextjs-"})
        
        if not containers:
            print("No Next.js containers found")
            logger.info("No Next.js containers to restore")
            return
        
        print(f"Found {len(containers)} Next.js containers")
        logger.info(f"Found {len(containers)} Next.js containers to restore")
        
        # Get the current vylos network
        try:
            vylos_network = client.networks.get("vylos_vylos_network")
        except docker_errors.NotFound:
            print("⚠ vylos_vylos_network not found - containers cannot start")
            logger.error("vylos_vylos_network not found")
            return
        
        for container in containers:
            print(f"\n→ {container.name}: {container.status}")
            
            try:
                if container.status != "running":
                    # Check if container is on the correct network
                    container.reload()  # Refresh container info
                    networks = container.attrs['NetworkSettings']['Networks']
                    
                    # Check if connected to current vylos network (by ID, not just name)
                    needs_reconnect = True
                    if 'vylos_vylos_network' in networks:
                        current_network_id = networks['vylos_vylos_network']['NetworkID']
                        # Verify the network ID actually exists
                        try:
                            client.networks.get(current_network_id)
                            needs_reconnect = False  # Network exists, no need to reconnect
                        except docker_errors.NotFound:
                            # Network ID doesn't exist, need to reconnect
                            pass
                    
                    # Disconnect from old/invalid networks and connect to current network
                    if needs_reconnect:
                        print(f"  Reconnecting to vylos_vylos_network...")
                        
                        # Disconnect from all networks
                        for old_network_name in list(networks.keys()):
                            try:
                                container.reload()
                                old_net = client.networks.get(old_network_name)
                                old_net.disconnect(container, force=True)
                                print(f"    Disconnected from: {old_network_name}")
                            except Exception as e:
                                print(f"    Could not disconnect from {old_network_name}: {e}")
                        
                        # Connect to current network
                        vylos_network.connect(container)
                        print(f"  ✓ Connected to vylos_vylos_network")
                    
                    print(f"  Starting stopped container...")
                    logger.info(f"Starting container: {container.name}")
                    container.start()
                    print(f"  ✓ Started")
                    logger.info(f"✓ Started {container.name}")
                else:
                    print(f"  ✓ Already running")
                    logger.info(f"✓ {container.name} already running")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                logger.error(f"Error starting {container.name}: {e}")
        
        print("\n" + "=" * 50)
        print("RESTORATION COMPLETE")
        print("=" * 50)
        logger.info("Container restoration completed")
        
    except Exception as e:
        logger.error(f"Error during container restoration: {e}")


@app.on_event("startup")
async def startup_event():
    """Run container restoration in background on startup"""
    print("\n" + "!" * 50)
    print("STARTUP EVENT TRIGGERED")
    print("!" * 50 + "\n")
    
    # Run in background thread to not block startup
    thread = threading.Thread(target=restore_nextjs_containers)
    thread.daemon = True
    thread.start()
    logger.info("Started container restoration in background")
    print("Background thread started\n")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "Welcome to Vylos API",
            "version": settings.VERSION,
            "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
        }
    )


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.VERSION
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )