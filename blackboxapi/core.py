import asyncio
import json
from websockets.client import connect
from typing import Dict, Union

from helpers import Controller, Caller, ENDPOINT_URL


class BlackboxAPI(Controller, Caller):
    def __init__(self, token: str) -> None:
        Caller.__init__(self)
        self.websocket = None
        print(self)
        print(type(self))
        self.alive = False
        self.token = token
        self.heartbeat_interval = 0
        self.tasks = set()

    async def run(self) -> None:
        self.websocket = await connect(f"ws://{ENDPOINT_URL}/ws/")
        self.alive = True
        while self.alive:
            try:
                message = await self.websocket.recv()
                print(message)
                task = asyncio.create_task(self._process(message))
                self.tasks.add(task)
            except Exception as e:
                print(e)
                break
        for task in self.tasks:
            task.cancel()
        asyncio.gather(*self.tasks, return_exceptions=True)

    async def _ping_timer(self):
        while self.alive:
            await asyncio.sleep((self.heartbeat_interval / 1000) // 4)
            ping_frame = {
                "op": 0x9,
                "data": None,
                "event": ""
            }
            send_data = json.dumps(ping_frame)
            await self.websocket.send(send_data)

    async def _process(self, message):
        data_frame: Dict[str, Union[str, Dict]] = json.loads(message)
        op: int = data_frame["op"]
        data = data_frame["data"]
        event: str = data_frame["event"]
        match op:
            case 0x0:  # TYPE_DISPATCH
                await self._process_event(data, event)
            case 0x2:  # TYPE_HELLO
                self.heartbeat_interval: int = data["heartbeatInterval"]
                identify_frame = {
                    "op": 0x1,
                    "data":  {"token": self.token},
                    "event": ""
                }
                send_data = json.dumps(identify_frame)
                await self.websocket.send(send_data)
            case 0x3:  # TYPE_READY
                ping_timer_task = asyncio.create_task(self._ping_timer())
                self.tasks.add(ping_timer_task)
                task = asyncio.create_task(self.on_ready())
                self.tasks.add(task)
            case 0x8:
                self.alive = False
                self.websocket.close()
            case 0xa:
                pass  # add thing for heart beat ack later


if __name__ == "__main__":
    api = BlackboxAPI(
        "0041f292d006dcce4263de6ad5dc2feb534843e85089d5277dbf08662dcf3bed")
    @api.event
    async def on_ready(self):
        print("READY")
    @api.event
    async def on_create_guild_message(self,data):
        print("WORKED")
        print("message", data)
        if data["content"] == "ping":
            await self.send_message(data["guild_id"], "pong")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(api.run())
