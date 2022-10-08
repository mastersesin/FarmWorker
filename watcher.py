import os
import threading
import time
import subprocess
import select
import telegram

EXIT_FLAG = False


def run(process, obj):
    global EXIT_FLAG
    last_event_time = int(time.time())
    while True:
        if EXIT_FLAG:
            os.abort(1)
        if int(time.time()) - last_event_time >= 10 * 60:
            last_event_time = int(time.time())
        if process.poll(1):
            data = obj.stdout.readline().decode()
            if 'harvester chia.harvester.harvester: ERROR' in data:
                bot.send_message(
                    chat_id=telegram_channel_id,
                    text=f'{data}'
                )
            if 'harvester chia.harvester.harvester: INFO' in data or 'harvester chia.plotting.plot_tools: INFO' in data:
                last_event_time = int(time.time())
                print(data.strip())
        time.sleep(0.01)


def run_rclone(process, obj):
    global EXIT_FLAG
    while True:
        if EXIT_FLAG:
            os.abort()
        if process.poll(1):
            data = obj.stdout.readline().decode()
            print(data.strip())
        time.sleep(0.01)


filename = '/root/.chia/mainnet/log/debug.log'
rclone_log_file = '/code/rclone_log.txt'
telegram_api_token = '1989791535:AAFFS4efdml_WehN6LwBXSnxRqtPbRG5X7Y'
telegram_channel_id = -584319866
bot = telegram.Bot(token=telegram_api_token)
f = subprocess.Popen(['tail', '-F', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
f_rclone = subprocess.Popen(['tail', '-F', rclone_log_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)
p_rclone = select.poll()
p_rclone.register(f_rclone.stdout)
threading.Thread(target=run, args=(p, f)).start()
threading.Thread(target=run_rclone, args=(p_rclone, f_rclone)).start()
