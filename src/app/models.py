from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    telegram_chat_id = Column(String(32), index=True, unique=True)
