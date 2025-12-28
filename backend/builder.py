import docker
import os
import shutil

# Initialize Docker Client
client = docker.from_env()

def deploy_app(git_url, app_name):
    # 1. Define where the files should land on your Laptop
    # This creates the absolute path: /Users/Zayed/Desktop/vylos-docker/projects/app-name
    host_work_dir = os.path.join(os.getcwd(), 'projects', app_name)
    
    # Clean slate: If folder exists, delete it so we don't have old files
    if os.path.exists(host_work_dir):
        shutil.rmtree(host_work_dir)
    os.makedirs(host_work_dir)

    print(f"🚀 Deploying {app_name} from {git_url}...")

    # 2. Run the Docker Container
    # We mount 'host_work_dir' (laptop) to '/output' (container)
    client.containers.run(
        image="node:18-alpine",
        command = f'sh -c "apk add --no-cache git && git clone --depth 1 {git_url} /app && cd /app && npm install && npm run build && (cp -r dist/* /output/ || cp -r build/* /output/)"',
        volumes={
            host_work_dir: {'bind': '/output', 'mode': 'rw'}
        },
        remove=True # Auto-delete container when done
    )

    print(f"✅ Success! App is live at http://{app_name}.localhost")