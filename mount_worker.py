import json
import os
import random
import subprocess
import signal
import sys
import threading
import time

MIN_MOUNT_TIME = 2 * 60 * 60
MAX_MOUNT_TIME = 6 * 60 * 60
SERVICE_ACCOUNT_ROOT_PATH = 'sa'
RCLONE_TEMPLATE = '''
[{remote_name}]
client_id = {client_id}
client_secret = {client_secret}
type = drive
scope = drive.readonly
token = {token} 
root_folder_id = {root_folder_id}
'''


def delete_remote_if_existed(remote_name):
    os.system(f'rclone config delete {remote_name}')


def add_rclone_token_to_rclone_config_file(remote_name, rclone_token, root_folder_id, client_id, client_secret):
    print(f'Rclone config info info {remote_name}-{rclone_token}-{root_folder_id}-{client_id}-{client_secret}')
    rclone_abs_path = subprocess.check_output('rclone config file'.split()).decode().split('\n')[1]

    command_return_code = os.system("echo '{}' >> {}".format(RCLONE_TEMPLATE.format(
        remote_name=remote_name,
        token=rclone_token,
        root_folder_id=root_folder_id,
        client_id=client_id,
        client_secret=client_secret
    ), rclone_abs_path))
    if command_return_code == 0:
        return True
    return False


def mount_drive(root_folder_id):
    remote_name = root_folder_id
    local_folder_name = root_folder_id
    print(f'Start mounting {remote_name} to {local_folder_name}')
    os.system('mkdir {}'.format(local_folder_name))
    # os.system('mkdir /tmp1/{}'.format(_local_farm_folder_path))
    command = f'rclone mount --contimeout=1s --multi-thread-streams=4096 ' \
              f'--log-file={remote_name}.txt --vfs-read-chunk-size=64K ' \
              f'--vfs-read-wait=1ms --buffer-size 0K ' \
              f'--drive-pacer-min-sleep=1ms {remote_name}: {local_folder_name}'
    os.system('fusermount -u {}'.format(local_folder_name))
    process = subprocess.Popen(command.split(' '))
    print(f'Mount done with process {process.pid}')
    return process.pid


def controller(root_folder_id, rclone_token, client_id, client_secret):
    while True:
        remote_name = root_folder_id
        print('Start delete remote if remote existed')
        delete_remote_if_existed(remote_name=remote_name)

        print('Start adding remote again')
        is_add_ok = add_rclone_token_to_rclone_config_file(
            remote_name=root_folder_id,
            rclone_token=rclone_token,
            root_folder_id=root_folder_id,
            client_id=client_id,
            client_secret=client_secret
        )

        if not is_add_ok:
            print('Cannot add rclone token into it config file')
            return

        print('Start mounting remote')
        threading.Thread(target=mount_drive, args=(root_folder_id,)).start()
        print(f'Start mounting done with process id: {mount_process_id}')

        while True:
            time.sleep(1)

        print('Sleep done start kill remote and start over again with new credential')
        os.kill(mount_process_id, signal.SIGKILL)
