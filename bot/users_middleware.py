from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from typing import Callable, Dict, Any, Awaitable

from user_manager import UserManager
from icecream import ic


class UsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_data = {
            "tg_user_id": data["event_from_user"].id,
            "first_name": data["event_from_user"].first_name,
            "last_name": data["event_from_user"].last_name,
            "username": data["event_from_user"].username,
            "referred_by": event.text.split(' ')[1] if event.text and len(event.text.split(' ')) > 1 else ''
        }
        user_manager = UserManager(data["session"])
        
        new_user = await user_manager.is_new_user(data["event_from_user"].id)
        data["new_user"] = new_user
        await user_manager.add_user_if_not_exists(user_data)
        data["session"] = user_manager.session
        return await handler(event, data)
