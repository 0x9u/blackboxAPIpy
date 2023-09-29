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
    
    async def get_guild(self, guild_id : str, /) -> Guild:
        guild = await self.caller.get_guild(guild_id)
        return Guild(**guild)

    async def get_friends(self) -> List[User]:
        users = await self.caller.get_friends()
        return [User(**user) for user in users]

    async def get_friend_requests(self) -> List[User]:
        users = await self.caller.get_friend_requests()
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
    
    async def get_user_by_name(self, username: str, /) -> User:
        user = await self.caller.get_user_by_name(username)
        return User(**user)

    async def get_bans(self, guild_id: str, /) -> List[User]:
        users = await self.caller.get_bans(guild_id)
        return [User(**user) for user in users]
    
    async def get_admins(self, guild_id: str, /) -> List[User]:
        users = await self.caller.get_admins(guild_id)
        return [User(**user) for user in users]

    async def get_members(self, guild_id: str, /) -> List[User]:
        users = await self.caller.get_members(guild_id)
        return [User(**user) for user in users]

    async def send_message(self, guild_id: str, message: str, /) -> None:
        await self.caller.send_message(guild_id, message)

    async def start_typing(self, guild_id : str, /) -> None:
        await self.caller.start_typing(guild_id)

    async def join_guild(self, guild_id: str, /) -> None:
        await self.caller.join_guild(guild_id)
    
    async def leave_guild(self, guild_id: str, /) -> None:
        await self.caller.leave_guild(guild_id)
    
    async def create_guild(self, name: str, save_chat : bool,/) -> None:
        await self.caller.create_guild(name, save_chat)

    async def edit_guild(self, guild_id: str, /, *, name: Optional[str] = None, save_chat: Optional[bool]= None, owner_id: Optional[str]= None) -> None:
        await self.caller.edit_guild(guild_id, name=name, save_chat=save_chat, owner_id=owner_id)
    
    async def delete_guild(self, guild_id: str, /) -> None:
        await self.caller.delete_guild(guild_id)
    
    async def create_dm(self, user_id: str, /) -> None:
        await self.caller.create_dm(user_id)
    
    async def delete_dm(self, dm_id: str, /) -> None:
        await self.caller.delete_dm(dm_id)
    
    async def add_friend(self, user_id: str, /) -> None:
        await self.caller.add_friend(user_id)
    
    async def add_friend_by_name(self, username: str, /) -> None:
        await self.caller.add_friend_by_name(username)
    
    async def remove_friend(self, user_id: str, /) -> None:
        await self.caller.remove_friend(user_id)
    
    async def accept_friend_request(self, user_id: str, /) -> None:
        await self.caller.accept_friend_request(user_id)
    
    async def decline_friend_request(self, user_id: str, /) -> None:
        await self.caller.decline_friend_request(user_id)
    
    async def block_user(self, user_id: str, /) -> None:
        await self.caller.block_user(user_id)
    
    async def unblock_user(self, user_id: str, /) -> None:
        await self.caller.unblock_user(user_id)
    
    async def ban_user(self, guild_id: str, user_id: str, /) -> None:
        await self.caller.ban_user(guild_id, user_id)
    
    async def unban_user(self, guild_id: str, user_id: str, /) -> None:
        await self.caller.unban_user(guild_id, user_id)
    
    async def kick_user(self, guild_id: str, user_id: str, /) -> None:
        await self.caller.kick_user(guild_id, user_id)
    
    async def edit_self(self, password : str, /, *, new_password : Optional[str] = None,username: Optional[str] = None, email : Optional[str] = None, options : Optional[int] = None) -> None:
        await self.caller.edit_self(password, new_password=new_password, username=username, email=email, options=options)
    



if __name__ == "__main__":
    api = Client(
        token="5e8e815647e5d12b235e32621d46021ed744e3d9723da24a8d2bac6ea60daa44")

    self_data = None

    @api.event
    async def ready(self: Client):
        global self_data
        self_data = await self.get_self()
        print(self_data)

    @api.event
    async def message_create(self: Client, data: Msg):
        print(data.author)
        print(data.author.name)
        if self_data is not None and self_data.id == data.author.id:
            return
        split_content = data.content.split(" ")
        command, *args = split_content
        if not command.startswith("!"):
            return
        command = command[1:]
        match command:
            case "ping":
                await self.send_message(data.guild_id, "pong")
            case "pong":
                guild_data = await self.get_guilds()
                for guild in guild_data["guilds"]:
                    await self.send_message(guild.id, "respond")
            case "data":
                user_data = await self.get_user(data.author.id)
                await self.send_message(data.guild_id, f"doxxed username:{user_data.name}, id: {user_data.id}, image_id: {user_data.image_id}")
            case "raise":
                raise Exception("test")
            case "last_msg":
                last_msg = await self.get_messages(data.guild_id, 0, 5)
                for msg in last_msg:
                    await self.send_message(data.guild_id, f"last msg: {msg.content} by {msg.author.name}")
            case "start_typing":
                await self.start_typing(data.guild_id)
            case "join_guild":
                try:
                    await self.join_guild(args[0])
                except Exception as e:
                    await self.send_message(data.guild_id, f"error: {e}")
                else:
                    await self.send_message(data.guild_id, f"joined server with invite link: {args[0]}")
            case "leave_guild":
                try:
                    await self.leave_guild(args[0])
                except Exception as e:
                    await self.send_message(data.guild_id, f"error: {e}")
                else:
                    await self.send_message(data.guild_id, f"left server with id: {args[0]}")
            case "make_owner":
                try:
                    await self.edit_guild(data.guild_id, owner_id=data.author.id)
                except Exception as e:
                    await self.send_message(data.guild_id, f"error: {e}")
                else:
                    await self.send_message(data.guild_id, f"made owner with id: {data.author.id}, username {data.author.name}")
            case "create_dm":
                username = args[0]
                try:
                    user = await self.get_user_by_name(username)
                    await self.create_dm(user.id)
                except Exception as e:
                    await self.send_message(data.guild_id, f"error: {e}")
                else:
                    await self.send_message(data.guild_id, f"created dm with {username}")
            case "accept_request":
                user_id = data.author.id
                try:
                    await self.accept_friend_request(user_id)
                except Exception as e:
                    await self.send_message(data.guild_id, f"error: {e}")
                else:
                    await self.send_message(data.guild_id, f"accepted friend request with id: {user_id}, username: {data.author.name}")
            case "decline_request":
                user_id = data.author.id
                try:
                    await self.decline_friend_request(user_id)
                except Exception as e:
                    await self.send_message(data.guild_id, f"error: {e}")
                else:
                    await self.send_message(data.guild_id, f"declined friend request with id: {user_id}, username: {data.author.name}")
            case "dm": #hangs for some reason on this
                username = args[0]
                message = " ".join(args[1:])
                dms = await self.get_guilds()
                dms = dms["dms"]
                dm_id = None
                for dm in dms:
                    if dm.user_info.name == username:
                        dm_id = dm.id
                        break
                try:
                    await self.send_message(dm_id, message)
                except Exception as e:
                    await self.send_message(data.guild_id, f"error: {e}")
                else:
                    await self.send_message(data.guild_id, f"sent dm to {username}")


    api.run()
''