import asyncio
import json
from websockets.client import connect
from traceback import print_exc
from typing import Dict, Union, Optional, List


from helpers import Controller, Caller, Tasks, ENDPOINT_URL
from events import Guild, Dm, User, Msg


class Client(Controller):
    def __init__(self, *, token: str) -> None:
        self.websocket = None
        self.loop = None

        self.token = token
        self.heartbeat_interval = 0
        self.tasks = Tasks()

        self.caller = Caller(token)

    def run(self) -> None:
        self.caller._start_session()
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        # TODO: suppress cancelled error
        try:
            self.loop.run_until_complete(self._loop())
        except asyncio.exceptions.CancelledError:
            pass
    async def _loop(self) -> None:
        self.websocket = await connect(f"ws://{ENDPOINT_URL}/ws/", ping_interval=None)
        while self.websocket.open:
            try:
                message = await self.websocket.recv()
                print(message)
                await self._process(message)
            except Exception as e:
                print("PRINTING ERROR")
                print_exc() 
        await self.tasks.stop_tasks()
        await self.caller._stop_session()

    async def _ping_timer(self):
        while self.websocket.open:
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
                self.tasks.create_task(self._ping_timer(), name="ping_timer")
                self.tasks.create_task(self.on_ready(), name="on_ready")
            case 0x8:
                self.websocket.close()
            case 0xa:
                pass  # add thing for heart beat ack later
    # connection shit
    # TODO: make iterator function for retrieving guilds if user is in thousand of guilds

    async def get_guilds(self) -> List[Guild]:
        guild_list = await self.caller.get_guilds()
        print(guild_list)
        return {
            "guilds": [Guild(**guild, dm=False) for guild in guild_list["guilds"]],
            "dms": [
                Dm(**dm) for dm in guild_list["dms"]
            ]
        }

    async def get_friends(self) -> List[User]:
        users = await self.caller.get_friends()
        return [User(**user) for user in users]

    async def get_messages(self, guild_id : str, time : int, limit : int, /) -> List[Msg]:
        msgs = await self.caller.get_messages(guild_id, time, limit)
        return [Msg(**msg) for msg in msgs]

    async def get_self(self) -> User:
        user = await self.caller.get_self()
        return User(**user)

    async def get_user(self, user_id: str, /) -> User:
        user = await self.caller.get_user(user_id)
        return User(**user)

    async def send_message(self, guild_id: str, message: str, /) -> None:
        await self.caller.send_message(guild_id, message)


if __name__ == "__main__":
    api = Client(
        token="0041f292d006dcce4263de6ad5dc2feb534843e85089d5277dbf08662dcf3bed")

    @api.event
    async def create_guild_message(self: Client, data: Msg):
        print(data.author)
        print(data.author.name)
        if data.author.name == "testing123":
            return
        if data.content == "ping":
            print("is ping?")
            await self.send_message(data.guild_id, "pong")
        elif data.content == "pong":
            guild_data = await self.get_guilds()
            print(guild_data)
            for guild in guild_data["guilds"]:
                await self.send_message(guild.id, "respond")
        elif data.content == "data":
            user_data = await self.get_user(data.author.id)
            await self.send_message(data.guild_id, f"doxxed username:{user_data.name}, id: {user_data.id}, image_id: {user_data.image_id}")
        elif data.content == "raise":
            raise Exception("test")
        elif data.content == "last_msg": # repeating bug
            last_msg = await self.get_messages(data.guild_id, 0, 5)
            for msg in last_msg:
                await self.send_message(data.guild_id, f"last msg: {msg.content} by {msg.author.name}")


    api.run()
''