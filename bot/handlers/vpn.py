from aiogram import Router, F, Bot
from aiogram.filters.command import CommandStart
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ContentType

from aiogram.types import PreCheckoutQuery,  LabeledPrice, successful_payment, SuccessfulPayment


from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Cancel, Select, Group, Back

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert


from database.models import User, Transaction, Subscription, Server
from database.engine import session_maker

from typing import Optional
import logging
from datetime import datetime as dt

from icecream import ic


from handlers.on_click import pay_btn, buy_btn, balance_btn, status_btn, config_btn



router = Router()


class MySG(StatesGroup):
    window1 = State()
    window2 = State()
    
    

async def available_locations(callback: CallbackQuery, data, dialog_manager: DialogManager):

    await dialog_manager.switch_to(MySG.window2)



async def get_locations(dialog_manager: DialogManager,**kwargs):
    async with session_maker() as session:
        # ic(dialog_manager, kwargs)
        query = select(Server.location)
        response = await session.execute(query)
        result = response.all()
        result = [item[0] for item in result]
        dialog_manager.dialog_data['location'] = result

    return {
        "location": result
    }






@router.message(F.successful_payment) 
@router.message(CommandStart(), F.chat.type == "private")
async def handle_subscribe(message: Message, dialog_manager: DialogManager, new_user: bool):

    if message.successful_payment:

        amount = message.successful_payment.total_amount
        
        async with session_maker() as session_:
            try:
                insert_query = insert(Transaction).values(tg_user_id = message.from_user.id,
                                                   provider_payment_charge_id = message.successful_payment.provider_payment_charge_id,
                                                   invoice_payload = message.successful_payment.invoice_payload,
                                                   telegram_payment_charge_id = message.successful_payment.telegram_payment_charge_id,
                                                   currency = message.successful_payment.currency,
                                                   amount = message.successful_payment.total_amount,
                                                   transaction_date = dt.now())
                await session_.execute(insert_query)
                
                if message.successful_payment.currency == 'XTR':
                    update_query = update(User).where(User.tg_user_id == int(message.from_user.id)).values(balance_xtr = User.balance_xtr + int(amount))
                    await session_.execute(update_query)
                
                await session_.commit()
            except Exception as e:
                logging.error(f"Ошибка при обновлении баланса пользователя: {e}")
                
                
        await message.answer(f"Баланс успешно пополнен на сумму {amount} {message.successful_payment.currency}")
    

    if dialog_manager.event.text:
        ref_code = dialog_manager.event.text.split(' ')[1] if len(dialog_manager.event.text.split(' ')) > 1 else ''
        username = message.from_user.username if message.from_user.username else 'пользователь без никнейма'
        async with session_maker() as session_:
            
            query = select(User.tg_user_id, User.username).where(User.referal_code == ref_code)
            res = await session_.execute(query)
            refered_by = res.all()
            
            
        if refered_by and new_user:
            refered_by_username =refered_by[0][1] if refered_by[0][1] else 'пользователь без никнейма'
            
            async with session_maker() as session_:
                query = update(User).where(User.tg_user_id.in_([int(message.from_user.id), int(refered_by[0][0])])).values(balance_rub = User.balance_rub + 100)
                await session_.execute(query)
                await session_.commit()
            await message.answer(f"Вас пригласил {refered_by_username} и вы получаете неделю бесплатного премиум доступа")
            try:
                await message.bot.send_message(chat_id=refered_by[0][0], text = f"По вашей ссылке зарегистрировался {username}, вы молодцы")
            except Exception as e:
                logging.info(f"Ошибка отправки сообщения пользователю {refered_by[0][0]}: {e}")
                
                
    await dialog_manager.start(MySG.window1, mode=StartMode.NORMAL)
    
    
    
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    
    
    
sel_locations = Select(
    text=Format("{item}"),
    id="main",
    item_id_getter=lambda x: x,
    items="location",
    on_click=config_btn,
)

    
dialog = Dialog(
    
    Window(
        
        Format("получить доступ к ВПН"),
        Button(Const("💰 Пополнить счет через telegram stars"), id="pay", on_click=pay_btn),
        Button(Const("💳 Узнать баланс"), id= "bal", on_click=balance_btn),
        Button(Const("🐺 Статус подписки"), id= "status", on_click=status_btn),
        Button(Const("🔐 Оплатить подписку со своего счета"), id="buy", on_click=buy_btn),
        Button(Const("🌍 Доступные сервера"), id = "serv", on_click=available_locations),
        state=MySG.window1,
        
    ),
    Window(Format("Выберите локацию"),
        Group(sel_locations, width=2),
        Back(text=Const("⏪назад")),
        state=MySG.window2,
        getter=get_locations,
    ),

)