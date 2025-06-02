from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from database.models import User
from datetime import datetime as dt
from icecream import ic

class UserManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_new_user(self, tg_user_id: int) -> bool:
        user = await self.session.get(User, tg_user_id)

        return user is None
    
    async def add_user_if_not_exists(self, user_data: dict):
        add_user_query = insert(User).values(
            tg_user_id=user_data['tg_user_id'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            username=user_data['username'],
            joined_at=dt.now(),
            referred_by = user_data['referred_by'],
            is_admin=False
        ).on_conflict_do_nothing()
        await self.session.execute(add_user_query)
        await self.session.commit()