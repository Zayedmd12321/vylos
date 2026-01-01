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
    # In-memory status cache to avoid DB queries
    _status_cache = {}
    
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
    
    def get_status(self, project_id: str) -> dict:
        """Get cached status for a project"""
        return self._status_cache.get(project_id, {'status': 'Building', 'domain': None})
    
    def update_status(self, project_id: str, status: str, domain: str = ""):
        """Update cached status for a project"""
        if project_id not in self._status_cache:
            self._status_cache[project_id] = {}
        self._status_cache[project_id]['status'] = status
        if domain:
            self._status_cache[project_id]['domain'] = domain
    
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
        
        # Initialize status cache
        self.update_status(project_id, 'Building')
        
        try:
            # Log start
            self.add_log(project_id, f"🚀 Starting deployment for {project_id}")
            
            # Get or create project (single query with commit)
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
                db.flush()  # Get ID without full commit
                self.add_log(project_id, f"✓ Created new project: {project_id}")
            else:
                setattr(project, 'status', "Building")
                self.add_log(project_id, f"✓ Updating existing project: {project_id}")
            
            # Commit only once at the start
            db.commit()
            
            # Prepare paths
            internal_work_dir = f"/app/projects/{project_id}"
            host_work_dir = f"{settings.HOST_PROJECTS_PATH}/{project_id}"
            
            if os.path.exists(internal_work_dir):
                shutil.rmtree(internal_work_dir)
                self.add_log(project_id, "✓ Cleaned old build directory")
            os.makedirs(internal_work_dir, exist_ok=True)
            
            # Clone and detect framework first
            self.add_log(project_id, f"📦 Repository: {git_url}")
            self.add_log(project_id, "📥 Cloning repository...")
            
            clone_cmd = (
                f'sh -c "apk add --no-cache git && '
                f'git clone --depth 1 {git_url} /output"'
            )
            
            clone_container = self.client.containers.run(
                image="node:20-alpine",
                command=clone_cmd,
                volumes={host_work_dir: {'bind': '/output', 'mode': 'rw'}},
                detach=True
            )
            
            for line in clone_container.logs(stream=True, follow=True):
                log_line = line.decode('utf-8').strip()
                print(f"[{project_id}] {log_line}")
            
            clone_result = clone_container.wait()
            clone_container.remove(force=True)
            
            if clone_result.get('StatusCode', 1) != 0:
                raise Exception("Failed to clone repository")
            
            self.add_log(project_id, "✓ Repository cloned successfully")
            
            # Detect framework
            framework = self._detect_framework(internal_work_dir)
            self.add_log(project_id, f"🔍 Detected framework: {framework.upper()}")
            
            # Update project with framework (don't commit yet, will batch with status update)
            setattr(project, 'framework', framework)
            
            # Deploy based on framework
            if framework == "nextjs":
                self._deploy_nextjs(project_id, internal_work_dir, host_work_dir, db, project)
            else:
                self._deploy_static(project_id, internal_work_dir, host_work_dir, db, project)
            
        except Exception as e:
            print(f"[ERROR] Deployment failed: {e}")
            self.add_log(project_id, f"❌ Deployment failed: {str(e)}")
            
            # Update status cache immediately
            self.update_status(project_id, 'Failed')
            
            if project:
                # Batch updates: status and build logs in single commit
                setattr(project, 'status', "Failed")
                setattr(project, 'build_logs', '\n'.join(self.get_logs(project_id)))
                db.commit()
                db.refresh(project)
        
        finally:
            # Clear logs from memory after saving to database
            self.clear_logs(project_id)
            db.close()
    
    def _deploy_static(self, project_id: str, internal_work_dir: str, host_work_dir: str, db: Session, project):
        """
        Deploy static site (React, Vue, HTML, etc.)
        
        How it works:
        1. Source code is already cloned to /app (host: ./projects/{project_id}/)
        2. If package.json exists: npm install && npm run build
        3. Find build output directory (dist, build, out, or public)
        4. Move ONLY the built files to /app root, delete source files
        5. Nginx serves files from /var/www/html/{project_id} (mapped to ./projects/{project_id}/)
        
        Result: Static HTML/CSS/JS files at ./projects/{project_id}/index.html (served by nginx)
        """
        self.add_log(project_id, "⏳ Building static assets...")
        
        # Build and replace source with output - all in the same directory
        build_cmd = (
            f'sh -c "cd /app && '
            f'if [ -f package.json ]; then '
            f'  echo \\"📦 Installing dependencies...\\" && '
            f'  npm install && '
            f'  echo \\"🔨 Running build...\\" && '
            f'  npm run build && '
            f'  echo \\"📂 Looking for build output...\\" && '
            # Check each possible build output directory
            f'  for dir in dist build out public; do '
            f'    if [ -d \\"$dir\\" ]; then '
            f'      echo \\"✓ Found build output in $dir\\" && '
            # Create temp directory, move build output there, clean /app, move output back
            f'      mkdir -p /tmp/build_output && '
            f'      cp -r \\"$dir\\"/* /tmp/build_output/ && '
            f'      find /app -mindepth 1 -maxdepth 1 ! -name \"$dir\" -exec rm -rf {{}} + && '
            f'      mv /tmp/build_output/* /app/ && '
            f'      rm -rf /tmp/build_output && '
            f'      echo \\"✓ Deployed built files to /app root\\" && '
            f'      ls -la /app && '
            f'      exit 0; '
            f'    fi; '
            f'  done; '
            f'  echo \\"⚠ No standard build directory found (dist/build/out/public)\\" && '
            f'  echo \\"Using source files as-is\\" && '
            f'  exit 0; '
            f'else '
            f'  echo \\"📄 No package.json - serving as static HTML\\" && '
            f'  ls -la /app && '
            f'  exit 0; '
            f'fi"'
        )
        
        # Mount only the project directory - build happens in place
        container = self.client.containers.run(
            image="node:20-alpine",
            command=build_cmd,
            volumes={host_work_dir: {'bind': '/app', 'mode': 'rw'}},
            detach=True
        )
        
        self.add_log(project_id, "✓ Build container started...")
        
        # Stream logs
        for line in container.logs(stream=True, follow=True):
            log_line = line.decode('utf-8').strip()
            print(f"[{project_id}] {log_line}")
            self.add_log(project_id, log_line)
        
        result = container.wait()
        container.remove(force=True)
        
        if result.get('StatusCode', 1) == 0:
            self.add_log(project_id, "✅ Build completed successfully!")
            self.add_log(project_id, f"📁 Static files ready at: ./projects/{project_id}/")
            self.add_log(project_id, f"🌐 Live at: http://{project_id}{settings.DOMAIN_SUFFIX}")
            
            # Update status cache immediately
            self.update_status(project_id, 'Live', f"{project_id}{settings.DOMAIN_SUFFIX}")
            
            # Batch all updates: status, domain, framework, and build logs in single commit
            setattr(project, 'status', "Live")
            setattr(project, 'domain', f"{project_id}{settings.DOMAIN_SUFFIX}")
            setattr(project, 'build_logs', '\n'.join(self.get_logs(project_id)))
            db.commit()
            db.refresh(project)
        else:
            raise Exception("Build failed")
    
    def _deploy_nextjs(self, project_id: str, internal_work_dir: str, host_work_dir: str, db: Session, project):
        """Deploy Next.js application with persistent container"""
        self.add_log(project_id, "⏳ Building Next.js application...")
        
        # Build the Next.js app
        build_cmd = (
            'sh -c "cd /app && npm install && npm run build"'
        )
        
        build_container = self.client.containers.run(
            image="node:20-alpine",
            command=build_cmd,
            volumes={host_work_dir: {'bind': '/app', 'mode': 'rw'}},
            detach=True
        )
        
        self.add_log(project_id, "✓ Build started...")
        
        # Stream build logs
        for line in build_container.logs(stream=True, follow=True):
            log_line = line.decode('utf-8').strip()
            print(f"[{project_id}] {log_line}")
            self.add_log(project_id, log_line)
        
        build_result = build_container.wait()
        build_container.remove(force=True)
        
        if build_result.get('StatusCode', 1) != 0:
            raise Exception("Next.js build failed")
        
        self.add_log(project_id, "✅ Build completed!")
        self.add_log(project_id, "🚀 Starting Next.js server...")
        
        # Stop any existing container for this project
        try:
            existing = self.client.containers.get(f"nextjs-{project_id}")
            existing.stop()
            existing.remove()
            self.add_log(project_id, "✓ Stopped old container")
        except:
            pass
        
        # Start Next.js server in a persistent container
        port = self._get_available_port()
        
        server_container = self.client.containers.run(
            image="node:20-alpine",
            command='sh -c "cd /app && npm start"',
            volumes={host_work_dir: {'bind': '/app', 'mode': 'ro'}},
            ports={'3000/tcp': port},
            name=f"nextjs-{project_id}",
            detach=True,
            auto_remove=False,
            network="vylos_vylos_network",
            restart_policy={"Name": "on-failure", "MaximumRetryCount": 5}  # Auto-restart on failure
        )
        
        # Update container to restart on failure
        server_container.update(restart_policy={'Name': 'on-failure', 'MaximumRetryCount': 5})
        
        self.add_log(project_id, f"✅ Next.js server started on port {port}")
        
        # Create nginx reverse proxy configuration
        self._create_nginx_proxy(project_id, port)
        self.add_log(project_id, f"✓ Configured nginx proxy")
        
        # Reload nginx to apply new config
        self._reload_nginx()
        self.add_log(project_id, f"🌐 Live at: http://{project_id}{settings.DOMAIN_SUFFIX}")
        
        # Update status cache immediately
        self.update_status(project_id, 'Live', f"{project_id}{settings.DOMAIN_SUFFIX}")
        
        # Batch all updates: status, domain, framework, and build logs in single commit
        setattr(project, 'status', "Live")
        setattr(project, 'domain', f"{project_id}{settings.DOMAIN_SUFFIX}")
        setattr(project, 'build_logs', '\n'.join(self.get_logs(project_id)))
        db.commit()
        db.refresh(project)
    
    def _create_nginx_proxy(self, project_id: str, port: int):
        """Create nginx reverse proxy configuration for Next.js app"""
        # Use /app/nginx-configs which is mounted from host
        nginx_config_dir = "/app/nginx-configs"
        os.makedirs(nginx_config_dir, exist_ok=True)
        
        config_content = f"""server {{
    listen 80;
    server_name {project_id}{settings.DOMAIN_SUFFIX};

    # Use Docker's internal DNS resolver for dynamic resolution
    resolver 127.0.0.11 valid=10s;
    
    location / {{
        # Use variable to force dynamic DNS resolution
        set $upstream_endpoint nextjs-{project_id}:3000;
        proxy_pass http://$upstream_endpoint;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        config_path = os.path.join(nginx_config_dir, f"{project_id}.conf")
        with open(config_path, 'w') as f:
            f.write(config_content)
    
    def _reload_nginx(self):
        """Reload nginx to apply new configuration"""
        try:
            nginx_container = self.client.containers.get("vylos-nginx-1")
            nginx_container.exec_run("nginx -s reload")
        except Exception as e:
            print(f"Warning: Could not reload nginx: {e}")
            # Try alternative container name
            try:
                nginx_container = self.client.containers.get("vylos_nginx_1")
                nginx_container.exec_run("nginx -s reload")
            except:
                print(f"Warning: Could not find nginx container")
    
    def _get_available_port(self) -> int:
        """Get an available port for deployment"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def _detect_framework(self, work_dir: str) -> str:
        """
        Detect the framework used in the project
        
        Args:
            work_dir: Working directory containing the project
            
        Returns:
            Framework name: 'nextjs', 'react', 'vue', 'static'
        """
        package_json_path = os.path.join(work_dir, "package.json")
        next_config_paths = [
            os.path.join(work_dir, "next.config.js"),
            os.path.join(work_dir, "next.config.mjs"),
            os.path.join(work_dir, "next.config.ts"),
        ]
        
        # Check for Next.js
        if any(os.path.exists(p) for p in next_config_paths):
            return "nextjs"
        
        # Check package.json for framework hints
        if os.path.exists(package_json_path):
            try:
                import json
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                    
                    if 'next' in deps:
                        return "nextjs"
                    elif 'react' in deps or 'react-scripts' in deps:
                        return "react"
                    elif 'vue' in deps:
                        return "vue"
            except:
                pass
        
        return "static"
