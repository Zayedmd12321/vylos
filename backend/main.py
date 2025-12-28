from fastapi import FastAPI, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel
import docker
import os
import shutil
from database import engine, SessionLocal # <--- Added SessionLocal

# 1. Database Setup
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
client = docker.from_env()

# --- Pydantic Models ---
class DeployRequest(BaseModel):
    git_url: str
    project_id: str

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- STARTUP EVENT (Fixes the owner_id=1 crash) ---
@app.on_event("startup")
def create_dummy_user():
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(models.User).filter(models.User.email == "test@vylos.com").first()
        if not user:
            print("👤 Creating dummy user (ID=1) for testing...")
            dummy_user = models.User(
                email="test@vylos.com", 
                hashed_password="fake_hash", 
                is_active=True
            )
            db.add(dummy_user)
            db.commit()
            print(f"✅ Dummy user created: ID={dummy_user.id}")
    except Exception as e:
        print(f"⚠️ Warning creating user: {e}")
    finally:
        db.close()

# --- THE REAL-TIME DEPLOY WORKER ---
def run_deploy(git_url: str, project_id: str):
    db = SessionLocal()
    print("\n" + "="*50)
    print(f"🚀 [START] Real-time Build for: {project_id}")
    print("="*50)

    container = None 

    try:
        # 1. DATABASE: Get or Create Project
        project = db.query(models.Project).filter(models.Project.name == project_id).first()
        if not project:
            # We use owner_id=1 which we created in startup
            project = models.Project(name=project_id, git_url=git_url, status="Building", owner_id=1)
            db.add(project)
        else:
            project.status = "Building"
        db.commit()

        # 2. FILESYSTEM SETUP
        internal_work_dir = f"/app/projects/{project_id}"
        # Make sure this env var matches your docker-compose volume path!
        host_base_path = os.getenv("HOST_PROJECTS_PATH", "D:/projects/vylos/backend/projects")
        host_work_dir = f"{host_base_path}/{project_id}"

        if os.path.exists(internal_work_dir):
            shutil.rmtree(internal_work_dir)
        os.makedirs(internal_work_dir, exist_ok=True)

        # 3. BUILD COMMAND
        build_cmd = (
            f'sh -c "apk add --no-cache git && '
            f'git clone --depth 1 {git_url} /app && '
            f'cd /app && '
            f'if [ -f package.json ]; then '
            f'  echo \\"Node.js project detected!\\" && '
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

        # 4. RUN DOCKER & STREAM LOGS
        container = client.containers.run(
            image="node:18-alpine",
            command=build_cmd,
            volumes={host_work_dir: {'bind': '/output', 'mode': 'rw'}},
            detach=True
        )

        for line in container.logs(stream=True, follow=True):
            print(f"[{project_id}] {line.decode('utf-8').strip()}")

        # 5. CHECK SUCCESS
        result = container.wait()
        exit_code = result.get('StatusCode', 1)

        if exit_code == 0:
            print(f"✅ [SUCCESS] Build finished.")
            project.status = "Live"
            project.domain = f"{project_id}.localhost"
        else:
            raise Exception(f"Container exited with code {exit_code}")

        db.commit()

    except Exception as e:
        print(f"❌ [ERROR] Deployment failed: {e}")
        project.status = "Failed"
        db.commit()
    
    finally:
        if container:
            try:
                container.remove(force=True)
                print("🧹 [CLEANUP] Builder removed.")
            except:
                pass
        db.close()
        print("="*50 + "\n")

# --- ENDPOINT ---
@app.post("/deploy")
async def deploy(request: DeployRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(run_deploy, request.git_url, request.project_id)
    return {
        "status": "Queued", 
        "message": f"Deployment started for {request.project_id}."
    }