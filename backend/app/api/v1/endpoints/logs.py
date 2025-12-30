"""
SSE (Server-Sent Events) endpoint for real-time deployment logs
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import json
from typing import AsyncGenerator

from app.core.dependencies import get_db
from app.db import models
from app.services.deployment_service import DeploymentService

router = APIRouter()


async def log_stream(project_name: str, user_id: int, db: Session) -> AsyncGenerator[str, None]:
    """
    Stream deployment logs in real-time using SSE
    """
    deployment_service = DeploymentService()
    last_position = 0
    max_retries = 120  # 120 * 2 seconds = 4 minutes max
    retries = 0
    
    # Send initial connection success
    yield f"data: {json.dumps({'type': 'connected', 'message': 'Stream connected'})}\n\n"
    
    while retries < max_retries:
        try:
            # Get project from database
            project = db.query(models.Project).filter(
                models.Project.name == project_name,
                models.Project.owner_id == user_id
            ).first()
            
            if not project:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Project not found'})}\n\n"
                break
            
            # Get logs from memory cache
            logs = deployment_service.get_logs(project_name)
            
            # Send new logs
            if logs and len(logs) > last_position:
                for log in logs[last_position:]:
                    yield f"data: {json.dumps({'type': 'log', 'message': log})}\n\n"
                last_position = len(logs)
            
            # Send status update
            status_data = {
                'type': 'status',
                'status': project.status,
                'domain': project.domain
            }
            yield f"data: {json.dumps(status_data)}\n\n"
            
            # If deployment finished, send completion and stop
            if project.status in ['Live', 'Failed']:
                final_data = {
                    'type': 'complete',
                    'status': project.status,
                    'domain': project.domain,
                    'url': f"http://{project.domain}" if project.domain else None
                }
                yield f"data: {json.dumps(final_data)}\n\n"
                break
            
            # Wait before next check
            await asyncio.sleep(1)
            retries += 1
            
            # Refresh database session
            db.refresh(project)
            
        except Exception as e:
            print(f"Error in log stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            break
    
    if retries >= max_retries:
        yield f"data: {json.dumps({'type': 'timeout', 'message': 'Deployment timeout'})}\n\n"


@router.get("/stream/{project_name}")
async def stream_deployment_logs(
    project_name: str,
    token: str = Query(..., description="JWT token for authentication"),
    db: Session = Depends(get_db)
):
    """
    Stream deployment logs in real-time using Server-Sent Events
    Auth via query parameter since EventSource doesn't support custom headers
    """
    # Verify token manually
    from app.core.security import verify_token
    
    try:
        print(f"Received token: {token[:20]}..." if len(token) > 20 else f"Received token: {token}")
        payload = verify_token(token)
        print(f"Token payload: {payload}")
        
        # Token uses "sub" for user_id
        user_id = payload.get("sub")
        if user_id:
            user_id = int(user_id)
        else:
            # Fallback to user_id if present
            user_id = payload.get("user_id")
        
        if not user_id:
            print("No user_id/sub in token payload")
            raise HTTPException(status_code=401, detail="Invalid token - no user identifier")
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")
    
    print(f"User ID: {user_id}, Project: {project_name}")
    
    # Check if project exists and belongs to user
    project = db.query(models.Project).filter(
        models.Project.name == project_name,
        models.Project.owner_id == user_id
    ).first()
    
    if not project:
        print(f"Project not found for user {user_id}")
        raise HTTPException(status_code=404, detail="Project not found")
    
    print(f"Starting SSE stream for project: {project_name}")
    
    return StreamingResponse(
        log_stream(project_name, user_id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )
