import requests

MAX_FOLDER_PER_DOCKER = 3

current_running_folder = 0
while True:
    if current_running_folder < MAX_FOLDER_PER_DOCKER:
        # Try ask server
        ask_request = requests.get()
        pass
