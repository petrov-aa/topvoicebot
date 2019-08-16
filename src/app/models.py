from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Chat(Base):
    """
    Объект чата. Смысл чата в том, чтобы хранить в нем состояние чата пользователя с ботом.
    """
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    telegram_chat_id = Column(String(32), index=True, unique=True)
    # Состояние чата пользователя с ботом
    state = Column(String(255))


class Voice(Base):
    """
    Войс.
    """
    __tablename__ = 'voice'
    id = Column(Integer, primary_key=True)
    file_id = Column(String(255))
    # Идентификатор телеграм автора войса
    author_id = Column(String(32))
    # Имя и фамилия отправителя войса. Кешируем, чтобы не ходить за каждым автором в телеграм
    author_first_name = Column(String(255))
    author_last_name = Column(String(255))
    # Идентификатор отправителя в бота
    sender_id = Column(Integer, ForeignKey("chat.id", ondelete="CASCADE"))
    sender = relationship("Chat", cascade="all, delete-orphan")
    title = Column(String(255))
