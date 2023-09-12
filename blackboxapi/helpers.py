import aiohttp
import asyncio
import json

ENDPOINT_URL = "localhost:8080/api"


class Controller:
    def event(self, func):
        print(self)
        print(type(self))
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Event must be a coroutine function")
        if not hasattr(self, func.__name__):
            raise AttributeError("Event not found")
        setattr(self, func.__name__, func)
        return func
    async def _process_event(self, data, event):
        match event: #can be shorten significantly by using __name__ getattr
            case "CREATE_GUILD":
                await self.on_create_guild(data)
            case "DELETE_GUILD":
                await self.on_delete_guild(data)
            case "UPDATE_GUILD":
                await self.on_update_guild(data)
            case "NOT_OWNER":
                await self.on_not_owner(data)
            case "NEW_OWNER":
                await self.on_new_owner(data)
            case "CREATE_INVITE":
                await self.on_create_invite(data)
            case "DELETE_INVITE":
                await self.on_delete_invite(data)
            case "CREATE_GUILD_MESSAGE":
                await self.on_create_guild_message(data)
            case "DELETE_GUILD_MESSAGE":
                await self.on_delete_guild_message(data)
            case "UPDATE_GUILD_MESSAGE":
                await self.on_update_guild_message(data)
            case "CREATE_DM":
                await self.on_create_dm(data)
            case "DELETE_DM":
                await self.on_delete_dm(data)
            case "CREATE_DM_MESSAGE":
                await self.on_create_dm_message(data)
            case "DELETE_DM_MESSAGE":
                await self.on_delete_dm_message(data)
            case "UPDATE_DM_MESSAGE":
                await self.on_update_dm_message(data)
            case "CLEAR_USER_DM_MESSAGES":
                await self.on_clear_user_dm_messages(data)
            case "USER_DM_TYPING":
                await self.on_user_dm_typing(data)
            case "ADD_FRIEND_REQUEST":
                await self.on_add_friend_request(data)
            case "REMOVE_FRIEND_REQUEST":
                await self.on_remove_friend_request(data)
            case "ADD_USER_FRIENDLIST":
                await self.on_add_user_friendlist(data)
            case "REMOVE_USER_FRIENDLIST":
                await self.on_remove_user_friendlist(data)
            case "CLEAR_USER_MESSAGES":
                await self.on_clear_user_messages(data)
            case "CLEAR_GUILD_MESSAGES":
                await self.on_clear_guild_messages(data)
            case "USER_TYPING":
                await self.on_user_typing(data)
            case "ADD_USER_GUILDLIST":
                await self.on_add_user_guildlist(data)
            case "REMOVE_USER_GUILDLIST":
                await self.on_remove_user_guildlist(data)
            case "ADD_USER_BANLIST":
                await self.on_add_user_banlist(data)
            case "REMOVE_USER_BANLIST":
                await self.on_remove_user_banlist(data)
            case "ADD_USER_GUILDADMIN":
                await self.on_add_user_guildadmin(data)
            case "REMOVE_USER_GUILDADMIN":
                await self.on_remove_user_guildadmin(data)
            case "LOG_OUT":
                await self.on_log_out(data)
            case "UPDATE_USER_INFO":
                await self.on_update_user_info(data)
            case "UPDATE_SELF_USER_INFO":
                await self.on_update_self_user_info(data)

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
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()

    async def send_message(self, guild_id: str, message: str) -> None:
        send_data = {
            "content": message
        }
        header = {
            "authorization" : self.token
        }
        print("sending msg")
        async with self.session.post(f"http://{ENDPOINT_URL}/guilds/{guild_id}/msgs", data=json.dumps(send_data), headers=header) as response:
            print("test")
            print(response.status)
            response.raise_for_status()
