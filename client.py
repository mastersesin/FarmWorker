import json
import os
import threading
import time

import requests
import telegram
from mount_worker import controller

MAX_FOLDER_PER_DOCKER = 3

WORKER_ID = os.environ["WORKER_ID"]
ENDPOINT = 'http://35.223.167.23:5000/'


def send_telegram_message(message):
    token = '1989791535:AAFFS4efdml_WehN6LwBXSnxRqtPbRG5X7Y'
    channel_id = -584319866
    bot = telegram.Bot(token=token)
    bot.send_message(
        chat_id=channel_id,
        text=f'{message}'
    )


def add_chia_folder(folder_id):
    os.system(f"chia-blockchain/venv/bin/chia plots add -d {folder_id}")


def worker():
    current_running_folder = 0
    while True:
        # Try ask server
        ask_folder_id_request = requests.get(f"{ENDPOINT}folder", params={"is_filter": True}).json()
        if ask_folder_id_request["status"]:
            if len(ask_folder_id_request["message"]) >= 1:
                ask_folder_id_obj = ask_folder_id_request["message"][0]
                ask_rclone_token_request = requests.get(f"{ENDPOINT}token", params={"is_filter": True}).json()
                if len(ask_rclone_token_request["message"]) >= 1:
                    ask_rclone_token_obj = ask_rclone_token_request["message"][0]
                    headers = {'Content-type': 'application/json'}
                    register_task = requests.post(f"{ENDPOINT}worker", json={
                        "rclone_token_id": str(ask_rclone_token_obj["id"]),
                        "folder_id": str(ask_folder_id_obj["id"]),
                        "worker_id": str(WORKER_ID)
                    }, headers=headers).json()
                    if register_task["status"]:
                        # RUN HERE
                        controller(
                            ask_folder_id_obj["folder_id"],
                            ask_rclone_token_obj["rclone_token"],
                            ask_rclone_token_obj["client_id"],
                            ask_rclone_token_obj["client_secret"]
                        )
                        print("Rclone-Added controller")
                        add_chia_folder(ask_folder_id_obj["folder_id"])
                        print("Rclone-Added chia folder")
                        current_running_folder += 1
                    else:
                        print(f'Controller-{register_task["reason"]}')

                else:
                    threading.Thread(target=send_telegram_message, args=("Folder is more than Rclone",)).start()
                    time.sleep(60)
            else:
                print("Rclone-Folder queue empty")
                time.sleep(60)
        time.sleep(60)
        requests.put(f"{ENDPOINT}worker", json={'worker_id': WORKER_ID})
