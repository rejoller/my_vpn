from aiogram import Router


def setup_routers() -> Router:
    from handlers import vpn
    from handlers.vpn import dialog
    from aiogram_dialog import setup_dialogs
    
   
    router = Router()
    
    router.include_router(vpn.router)
    router.include_router(dialog)

    setup_dialogs(router)
    
    
    return router