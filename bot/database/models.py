from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import ForeignKey, String, BIGINT, TIMESTAMP, DateTime, BOOLEAN, INTEGER

class Base(DeclarativeBase):
    pass



class Users(Base):
    __tablename__ = 'user_'
    tg_user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    vpn_uidd: Mapped[int] = mapped_column(BIGINT, nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(200), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    joined_at: Mapped[DateTime] = mapped_column(TIMESTAMP)
    is_admin: Mapped[bool] = mapped_column(BOOLEAN)
    is_subscriber: Mapped[bool] = mapped_column(BOOLEAN)
    

    
    





    
    
    
    
    
    
    
    
    
    
    
    
