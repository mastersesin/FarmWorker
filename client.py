import asyncio
import websockets
import json

REGISTER = 'register'
ASK_TASK = 'ask_task'


async def main():
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        await websocket.send(REGISTER)
        res_register = await websocket.recv()
        json_res_register = json.loads(res_register)
        if json_res_register['status'] == 'ok':
            await websocket.send(ASK_TASK)
            res_task = await websocket.recv()
            json_res_task = json.loads(res_task)


asyncio.run(main())
