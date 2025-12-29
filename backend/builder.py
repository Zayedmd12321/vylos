import docker
import os
import shutil

# Initialize Docker Client
client = docker.from_env()

def deploy_app(git_url, app_name):
    host_work_dir = os.path.join(os.getcwd(), 'projects', app_name)
    
    if os.path.exists(host_work_dir):
        shutil.rmtree(host_work_dir)
    os.makedirs(host_work_dir)

    print(f"Deploying {app_name} from {git_url}...")

    client.containers.run(
        image="node:18-alpine",
        command = f'sh -c "apk add --no-cache git && git clone --depth 1 {git_url} /app && cd /app && npm install && npm run build && (cp -r dist/* /output/ || cp -r build/* /output/)"',
        volumes={
            host_work_dir: {'bind': '/output', 'mode': 'rw'}
        },
        remove=True
    )

    print(f"Success! App is live at http://{app_name}.localhost")