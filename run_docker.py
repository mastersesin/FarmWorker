# sudo mkdir -p /etc/systemd/system/docker.service.d
# /etc/systemd/system/docker.service.d/docker-service-override.conf
# [Service]
# Environment="GOOGLE_APPLICATION_CREDENTIALS=/home/mastersesin12345/.config/gcloud/application_default_credentials.json"

import subprocess
import time

project_name = subprocess.check_output('gcloud config get-value project'.split()).strip().decode()
instance_name = subprocess.check_output('hostname'.split()).strip().decode()
docker_id = f'{project_name}:{instance_name}'
subprocess.Popen('sudo docker build . -t farm-worker'.split(' ')).wait()
for i in range(5):
    docker_cmd = f'sudo docker run -e WORKER_ID={docker_id}:host_{i} --log-driver=gcplogs ' \
                 f'--log-opt gcp-project=bright-seer-140205 ' \
                 f'--log-opt labels=worker_id --label worker_id={docker_id}:host_{i} ' \
                 f'--privileged -d farm-worker host_{i}'
    subprocess.Popen(docker_cmd.split(' ')).wait()
    time.sleep(5)
