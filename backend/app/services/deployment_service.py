"""
Deployment Service - Business logic for Docker deployments
"""
import os
import shutil
import docker
from typing import Optional
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import SessionLocal
from app.core.config import settings
from app.services.project_service import ProjectService


class DeploymentService:
    """Deployment service for building and deploying projects"""
    
    # In-memory log storage (in production, use Redis)
    _logs_cache = {}
    
    def __init__(self):
        """Initialize Docker client"""
        import os
        # Ensure DOCKER_HOST is set
        if not os.getenv('DOCKER_HOST'):
            os.environ['DOCKER_HOST'] = 'unix:///var/run/docker.sock'
        
        try:
            # Use from_env which respects DOCKER_HOST environment variable
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            print("✓ Docker client initialized successfully")
        except Exception as e:
            print(f"Failed to connect to Docker: {e}")
            print(f"DOCKER_HOST: {os.getenv('DOCKER_HOST')}")
            print(f"Socket exists: {os.path.exists('/var/run/docker.sock')}")
            raise Exception(f"Could not connect to Docker daemon. Error: {str(e)}")
    
    def add_log(self, project_id: str, message: str):
        """Add log message to cache"""
        if project_id not in self._logs_cache:
            self._logs_cache[project_id] = []
        self._logs_cache[project_id].append(message)
    
    def get_logs(self, project_id: str) -> list:
        """Get logs from cache"""
        return self._logs_cache.get(project_id, [])
    
    def clear_logs(self, project_id: str):
        """Clear logs for a project"""
        if project_id in self._logs_cache:
            del self._logs_cache[project_id]
    
    def run_deployment(
        self,
        git_url: str,
        project_id: str,
        user_id: int
    ) -> None:
        """
        Run deployment in background
        
        Args:
            git_url: Git repository URL
            project_id: Project identifier
            user_id: User ID
        """
        db = SessionLocal()
        print(f"\n[START] Build for: {project_id}")
        container = None
        project = None
        
        # Clear old logs
        self.clear_logs(project_id)
        
        try:
            # Log start
            self.add_log(project_id, f"🚀 Starting deployment for {project_id}")
            
            # Get or create project
            project = db.query(models.Project).filter(
                models.Project.name == project_id
            ).first()
            
            if not project:
                project = models.Project(
                    name=project_id,
                    repo_url=git_url,
                    status="Building",
                    owner_id=user_id
                )
                db.add(project)
                self.add_log(project_id, f"✓ Created new project: {project_id}")
            else:
                setattr(project, 'status', "Building")
                self.add_log(project_id, f"✓ Updating existing project: {project_id}")
            
            db.commit()
            
            # Prepare paths
            internal_work_dir = f"/app/projects/{project_id}"
            host_work_dir = f"{settings.HOST_PROJECTS_PATH}/{project_id}"
            
            if os.path.exists(internal_work_dir):
                shutil.rmtree(internal_work_dir)
                self.add_log(project_id, "✓ Cleaned old build directory")
            os.makedirs(internal_work_dir, exist_ok=True)
            
            # Build command
            build_cmd = self._get_build_command(git_url)
            self.add_log(project_id, f"📦 Repository: {git_url}")
            self.add_log(project_id, "⏳ Pulling Docker image...")
            
            # Run container
            container = self.client.containers.run(
                image="node:20-alpine",
                command=build_cmd,
                volumes={host_work_dir: {'bind': '/output', 'mode': 'rw'}},
                detach=True
            )
            
            self.add_log(project_id, "✓ Container started")
            self.add_log(project_id, "📥 Cloning repository...")
            
            # Stream logs and store them in cache
            for line in container.logs(stream=True, follow=True):
                log_line = line.decode('utf-8').strip()
                print(f"[{project_id}] {log_line}")
                self.add_log(project_id, log_line)
            
            # Check result
            result = container.wait()
            
            if result.get('StatusCode', 1) == 0:
                print(f"[SUCCESS] Build finished.")
                self.add_log(project_id, "✅ Build completed successfully!")
                self.add_log(project_id, f"🌐 Deploying to: {project_id}.localhost")
                ProjectService.update_project_status(
                    db=db,
                    project=project,
                    status="Live",
                    domain=f"{project_id}.localhost"
                )
            else:
                self.add_log(project_id, "❌ Build failed with error code")
                raise Exception("Container exited with error code")
        
        except Exception as e:
            print(f"[ERROR] Deployment failed: {e}")
            self.add_log(project_id, f"❌ Deployment failed: {str(e)}")
            if project:
                ProjectService.update_project_status(
                    db=db,
                    project=project,
                    status="Failed"
                )
        
        finally:
            if container:
                try:
                    container.remove(force=True)
                except:
                    pass
            db.close()
    
    @staticmethod
    def _get_build_command(git_url: str) -> str:
        """
        Generate build command for Docker container
        
        Args:
            git_url: Git repository URL
            
        Returns:
            Shell command string
        """
        return (
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
