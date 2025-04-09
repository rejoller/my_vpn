from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ContentType

from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format





router = Router()


class MySG(StatesGroup):
    window1 = State()
    window2 = State()
    
    
    
    
    
@router.message(CommandStart(), F.chat.type == "private")
async def handle_subscribe(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.window1, mode=StartMode.RESET_STACK)
    
    
    
    
dialog = Dialog(
    
    Window(
        
        Format("получить доступ к ВПН"),
        state=MySG.window1
    ))