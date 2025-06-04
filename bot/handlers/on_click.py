
from aiogram.types import CallbackQuery

from aiogram.types import LabeledPrice


from aiogram_dialog import DialogManager


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert

import ctypes
import uuid
from database.models import User, Subscription, Server
from database.engine import session_maker

from typing import Optional
import logging
from datetime import datetime as dt

from icecream import ic
from datetime import timedelta

from config import GO_FILE_PATH, API_ADDRESS, API_PORT, PBK, SHORT_VPN_ID







async def balance_btn(callback: CallbackQuery, dialog_manager: DialogManager, data: None):
    async with session_maker() as session:
        # ic(callback, dialog_manager, data)
        ic(data.find('location'))
        ic(data.dialog_data)
        query = select(User.balance_xtr).where(User.tg_user_id == int(callback.from_user.id))
        response = await session.execute(query)
        result = response.one()
        await callback.answer(f'Ваш баланс {result[0]} tg stars ⭐️', show_alert=True)
        
        
        
async def status_btn(callback: CallbackQuery, dialog_manager: DialogManager, data: None):
    async with session_maker() as session:

        query = select(func.max(Subscription.end_date)).where(Subscription.tg_user_id == int(callback.from_user.id))
        response = await session.execute(query)
        result = response.one()
        if result[0] is None:
            await callback.answer('У вас нет подписки 🤨', show_alert=True)
            return
        result = dt.strftime(result[0], "%d.%m.%Y")

        await callback.answer(f'Ваша подписка  действует до {result}', show_alert=True)
        
        

        
         
    
async def pay_btn(callback: CallbackQuery, session: AsyncSession, dialog_manager: DialogManager, data: Optional[dict] = None):
    prices = [LabeledPrice(label="XTR", amount=1)]
    await callback.message.answer_invoice(
            title="Пополнить счет с помощью telegram stars",
            description="Пополнить на 1 telegram stars",
            payload="100_stars",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="start_parameter_here"
        )
    
    
async def buy_btn(callback: CallbackQuery, dialog_manager: DialogManager, data):
    async with session_maker() as session:
        query = select(User.balance_xtr).where(User.tg_user_id == int(callback.from_user.id))
        response = await session.execute(query)
        result = response.one()
        if result[0] < 1:
            await callback.answer(f'Ваш баланс {result[0]} звезд😳 пополните счет', show_alert=True)
            return
        
        email = str(callback.from_user.id)
        email = email + "22"
        vpn_uuid = str(uuid.uuid4())
        query_balance_upd = update(User).where(User.tg_user_id == int(callback.from_user.id)).values(balance_xtr = User.balance_xtr - 1, vpn_uuid=vpn_uuid)
        try:
            address = f"{API_ADDRESS}:{API_PORT}"
            lib = ctypes.CDLL(GO_FILE_PATH)
            lib.InitClient.argtypes = [ctypes.c_char_p]
            lib.InitClient(address.encode('utf-8'))
            lib.addUser.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            lib.addUser.restype = ctypes.c_char_p
            lib.addUser(email.encode('utf-8'), vpn_uuid.encode('utf-8'))
            
            subscription_upd_query = insert(Subscription).values(tg_user_id = callback.from_user.id,
                                            start_date = dt.now(),
                                            end_date = dt.now() + timedelta(days=30))

            
            await session.execute(query_balance_upd)
            await session.execute(query)
            await session.execute(subscription_upd_query)
            await session.commit()
            
            await callback.message.answer('Покупка совершена, спасибо☺️')
            
        except Exception as e:
            logging.error(f"Ошибка при добавлении подписки: {e}")
            await session.rollback()
            await callback.message.answer('Ошибка при покупке, попробуйте позже')
            
            
            
async def config_btn(callback: CallbackQuery, dialog_manager: DialogManager, *args, **kwargs):
    async with session_maker() as session:
        short_name_location = str.split(callback.data, ':')[1]
        query = select(User.vpn_uuid).where(User.tg_user_id == int(callback.from_user.id))
        response = await session.execute(query)
        result = response.one()
        ic(result)
        if not result[0]:
            await callback.answer('Сначала нужно купить подписку☝️😡', show_alert=True)
            return
        vpn_uuid = result[0]
        
        query = select(Server.address).where(Server.location == short_name_location)
        response = await session.execute(query)
        
        address = response.one()[0]
        

    url = f"""vless://{vpn_uuid}@{address}:443?security=reality&encryption=none&pbk={PBK}&headerType=none&fp=chrome&type=tcp&flow=xtls-rprx-vision&sni=www.microsoft.com&sid={SHORT_VPN_ID}#CreengeVPNBot"""
    await callback.message.answer(text= f"""
                                  Ваш конфиг <pre>{url}</pre>\n\n<b>Как подключиться?</b>\n1. Скопируйте ключ.\n\
2. Откройте Hiddify v2RayTun(или аналогичный клиент).\n\
3. Нажмите ➕ (Добавить)\n4. 'Добавить из буфера обмена'.\n\
5. Подключение завершено, пользуйтесь ❤️""", parse_mode='HTML')