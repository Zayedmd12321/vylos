from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel
import docker
import os
import shutil
from database import engine, SessionLocal
from config import settings
from auth import router as auth_router, get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = docker.from_env()

app.include_router(auth_router)

class DeployRequest(BaseModel):
    git_url: str
    project_id: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_deploy(git_url: str, project_id: str, user_id: int):
    db = SessionLocal()
    print("\n" + "="*50)
    print(f"[START] Real-time Build for: {project_id}")
    print("="*50)
    container = None

    try:
        # 1. Create/Update Project with REAL User ID
        project = db.query(models.Project).filter(models.Project.name == project_id).first()
        if not project:
            project = models.Project(
                name=project_id, 
                git_url=git_url, 
                status="Building", 
                owner_id=user_id
            )
            db.add(project)
        else:
            setattr(project, 'status', "Building")
        db.commit()

        internal_work_dir = f"/app/projects/{project_id}"
        host_work_dir = f"{settings.HOST_PROJECTS_PATH}/{project_id}"

        if os.path.exists(internal_work_dir):
            shutil.rmtree(internal_work_dir)
        os.makedirs(internal_work_dir, exist_ok=True)

        build_cmd = (
            f'sh -c "apk add --no-cache git && '
            f'git clone --depth 1 {git_url} /app && '
            f'cd /app && '
            f'if [ -f package.json ]; then '
            f'  echo \\"React project detected!\\" && '
            f'  npm install && npm run build && '
            f'  for dir in dist build out public; do '
            f'    if [ -d \\"$dir\\" ]; then '
            f'      cp -r \\"$dir\\"/* /output/ && exit 0; '
            f'    fi; '
            f'  done; '
            f'  cp -r ./* /output/; '
            f'else '
            f'  echo \\"Static HTML project detected!\\" && cp -r * /output/; '
            f'fi"'
        )

        container = client.containers.run(
            image="node:18-alpine",
            command=build_cmd,
            volumes={host_work_dir: {'bind': '/output', 'mode': 'rw'}},
            detach=True
        )

        print("\n--- BUILD LOGS ---")
        for line in container.logs(stream=True, follow=True):
            print(f"[{project_id}] {line.decode('utf-8').strip()}")

        result = container.wait()
        if result.get('StatusCode', 1) == 0:
            print(f"[SUCCESS] Build finished.")
            setattr(project, 'status', "Live")
            setattr(project, 'domain', f"{project_id}.localhost")
        else:
            raise Exception("Container exited with error code")
        db.commit()

    except Exception as e:
        print(f"[ERROR] Deployment failed: {e}")
        if project is not None:
            setattr(project, 'status', "Failed")
            db.commit()
    finally:
        if container:
            try: container.remove(force=True)
            except: pass
        db.close()
        print("="*50 + "\n")

@app.post("/deploy")
async def deploy(
    request: DeployRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing = db.query(models.Project).filter(models.Project.name == request.project_id).first()
    if existing is not None and existing.owner_id != current_user.id:
         raise HTTPException(status_code=400, detail="Project name already taken")

    background_tasks.add_task(run_deploy, request.git_url, request.project_id, current_user.id)
    
    return {
        "status": "Queued", 
        "message": f"Deployment started for {request.project_id}",
        "user": current_user.email
    }