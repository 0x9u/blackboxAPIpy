import aiohttp
import asyncio
import json
from typing import List, Dict, Union, Optional, Any
from events import Guild, Msg, User, Dm

ENDPOINT_URL = "localhost:8080/api"

JSON_CONTENT = "application/json"
FORM_CONTENT = "application/x-www-form-urlencoded"


class Tasks:
    def __init__(self):
        self._tasks: List[asyncio.Task] = set()

    def create_task(self, coro, *, name):
        task = asyncio.create_task(coro, name=name)
        # i honestly cannot believe that exceptions are not raised in async tasks
        # wtf

        def task_finish(task):
            self._tasks.remove(task)
            if task.exception() is not None:
                raise task.exception()
        task.add_done_callback(task_finish)
        self._tasks.add(task)
    async def stop_tasks(self):
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)


class Controller:
    def event(self, coro):
        name = "on_"+coro.__name__
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("Event must be a coroutine function")
        if not hasattr(self, name):
            raise AttributeError("Event not found")
        # coro.__get__ required for calling it as a method
        # otherwise it calls a regular function
        setattr(self, name, coro.__get__(self))
        return coro

    async def _process_event(self, data, event):
        name = "on_"+event.lower()
        data_type = event.lower().split("_")[-1]
        match data_type:
            case "guild":
                data = Guild(**data)
            case "dm":
                data = Dm(**data)
            case "message":
                data = Msg(**data)
            case "user":
                data = User(**data)
            case _:
                print(f"Unknown event type {data_type}")
        try:
            coro = getattr(self, name)
        except AttributeError:
            print(f"Unidentified event: {event}")
        else:
            self.tasks.create_task(coro(data), name=name)

    async def on_ready(self) -> None:
        """
        Perform actions when the bot is ready.

        Returns:
            None
        """
        pass

    async def on_create_guild(self, data) -> None:
        """
        A function to handle the event when a guild is created.

        This function is called asynchronously and does not take any parameters.

        Returns:
            None
        """
        pass

    async def on_delete_guild(self, data) -> None:
        """
        A function to handle the event when a guild is deleted.

        This function is called asynchronously and does not take any parameters.

        Returns:
            None
        """
        pass

    async def on_update_guild(self, data) -> None:
        """
        A function to handle the event when a guild is updated.

        This function is called asynchronously and does not take any parameters.

        Returns:
            None
        """
        pass

    async def on_not_owner(self, data) -> None:
        pass

    async def on_new_owner(self, data) -> None:
        pass

    async def on_create_invite(self, data) -> None:
        pass

    async def on_delete_invite(self, data) -> None:
        pass

    async def on_create_guild_message(self, data) -> None:
        pass

    async def on_delete_guild_message(self, data) -> None:
        pass

    async def on_update_guild_message(self, data) -> None:
        pass

    async def on_create_dm(self, data) -> None:
        pass

    async def on_delete_dm(self, data) -> None:
        pass

    async def on_create_dm_message(self, data) -> None:
        pass

    async def on_delete_dm_message(self, data) -> None:
        pass

    async def on_update_dm_message(self, data) -> None:
        pass

    async def on_clear_user_dm_messages(self, data) -> None:
        pass

    async def on_user_dm_typing(self, data) -> None:
        pass

    async def on_add_friend_request(self, data) -> None:
        pass

    async def on_remove_friend_request(self, data) -> None:
        pass

    async def on_add_user_friendlist(self, data) -> None:
        pass

    async def on_remove_user_friendlist(self, data) -> None:
        pass

    async def on_clear_user_messages(self, data) -> None:
        pass

    async def on_clear_guild_messages(self, data) -> None:
        pass

    async def on_user_typing(self, data) -> None:
        pass

    async def on_add_user_guildlist(self, data) -> None:
        pass

    async def on_remove_user_guildlist(self, data) -> None:
        pass

    async def on_add_user_banlist(self, data):
        pass

    async def on_remove_user_banlist(self, data) -> None:
        pass

    async def on_add_user_guildadmin(self, data) -> None:
        pass

    async def on_remove_user_guildadmin(self, data) -> None:
        pass

    async def on_log_out(self, data) -> None:
        pass

    async def on_update_user_info(self, data) -> None:
        pass

    async def on_update_self_user_info(self, data) -> None:
        pass


class Caller:
    def __init__(self, token: str) -> None:
        self.token = token
        self.session = None
    
    def _start_session(self):
        self.session = aiohttp.ClientSession()
    
    async def _stop_session(self):
        await self.session.close()

    async def _request(self, request_type: str, route: str, /, *, data: Optional[Dict] = None, content_type: str = JSON_CONTENT) -> Any:
        url = f"http://{ENDPOINT_URL}{route}"
        headers = {
            "authorization": self.token,
            "content-type": content_type
        }
        if data is not None:
            data = json.dumps(data)
        async with self.session.request(request_type, url, headers=headers,
                                        data=data if request_type != "GET" else None,
                                        params=data if request_type == "GET" else None
                                        ) as response:
            response.raise_for_status()
            if request_type == "GET":
                return await response.json()

    async def get_guilds(self) -> List[Dict[str, Union[str, Dict]]]:
        return await self._request("GET", "/users/@me/guilds")

    async def get_messages(self, guild_id: str, time: int, limit: int) -> List[Dict[str, Union[str, Dict]]]:
        send_data = {
            "time": str(time) if time != 0 else "",
            "limit": str(limit)
        }
        return await self._request("GET", f"/guilds/{guild_id}/msgs", data=send_data)

    async def get_friends(self) -> List[Dict[str, str]]:
        return await self._request("GET", "/users/@me/friends")

    async def get_self(self) -> Dict[str, str]:
        return await self._request("GET", "/users/@me")

    async def get_user(self, user_id: str) -> Dict[str, str]:
        return await self._request("GET", f"/users/{user_id}")

    async def send_message(self, guild_id: str, message: str, /) -> None:
        send_data = {
            "content": message
        }
        print("sending msg")
        await self._request("POST", f"/guilds/{guild_id}/msgs", data=send_data)
