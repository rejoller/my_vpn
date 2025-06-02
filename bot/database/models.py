from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import ForeignKey, String, BIGINT, TIMESTAMP, DateTime, BOOLEAN, INTEGER

import string
import random

class Base(DeclarativeBase):
    pass


def generate_referral_code(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


class User(Base):
    __tablename__ = 'user_'
    tg_user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    vpn_uuid: Mapped[int] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(200), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    joined_at: Mapped[DateTime] = mapped_column(TIMESTAMP)
    referal_code: Mapped[str] = mapped_column(String(255), default=generate_referral_code)
    referred_by: Mapped[str] = mapped_column(String(255), nullable=True)
    is_admin: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    is_premium_user: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    balance_rub: Mapped[int] = mapped_column(INTEGER, default=0)
    balance_xtr: Mapped[int] = mapped_column(INTEGER, default=0)
    
    
    
    
class Subscription(Base):
    __tablename__ = 'subscription'
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(ForeignKey('user_.tg_user_id'))
    start_date: Mapped[DateTime] = mapped_column(TIMESTAMP)
    end_date: Mapped[DateTime] = mapped_column(TIMESTAMP)
    
    
class Transaction(Base):
    __tablename__ = 'transaction'
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(ForeignKey('user_.tg_user_id'))
    provider_payment_charge_id: Mapped[str] = mapped_column(String(255), nullable=True)
    invoice_payload: Mapped[str] = mapped_column(String(255), nullable=True)
    telegram_payment_charge_id: Mapped[str] = mapped_column(String(255), nullable=True)
    currency: Mapped[int] = mapped_column(String(255))
    amount: Mapped[int] = mapped_column(INTEGER)
    transaction_date: Mapped[DateTime] = mapped_column(TIMESTAMP)

    
class Server(Base):
    __tablename__ = 'server'
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(64))
    port: Mapped[int] = mapped_column(INTEGER)
    caption: Mapped[str] = mapped_column(String(255))
    hosting_provider: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))