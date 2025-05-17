import datetime
from sqlalchemy import (
    BigInteger, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.db_core import Base

class AccountSession(Base):
    __tablename__ = "account_sessions"
    __table_args__ = (
        UniqueConstraint("bot_user_id", "tg_account_id", name="uq_account_sessions_bot_user_id_tg_account_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    bot_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.id", ondelete="CASCADE"), nullable=False
    )
    tg_account_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tg_accounts.id"), nullable=False  # Без ondelete="CASCADE"!
    )
    session_data: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    bot_user = relationship(
        "BotUser",
        back_populates="sessions",
        overlaps="accounts"  # Добавляем overlaps
    )
    tg_account = relationship(
        "TGAccount",
        back_populates="sessions",
        overlaps="users"  # Добавляем overlaps
    )


class BotUser(Base):
    __tablename__ = "bot_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship(
        "AccountSession",
        back_populates="bot_user",
        overlaps="accounts",  # Добавляем overlaps
        cascade="all, delete-orphan"
    )
    accounts = relationship(
        "TGAccount",
        secondary="account_sessions",
        primaryjoin="BotUser.id == AccountSession.bot_user_id",
        secondaryjoin="TGAccount.id == AccountSession.tg_account_id",
        back_populates="users",
        viewonly=True,
        overlaps="sessions"
    )
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    dossiers = relationship("Dossier", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("Setting", back_populates="user", cascade="all, delete-orphan")
    statistics = relationship("Statistic", back_populates="user", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")


class TGAccount(Base):
    __tablename__ = "tg_accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship(
        "AccountSession",
        back_populates="tg_account",
        overlaps="users",  # Добавляем overlaps
        cascade="all, delete-orphan"
    )
    users = relationship(
        "BotUser",
        secondary="account_sessions",
        primaryjoin="TGAccount.id == AccountSession.tg_account_id",
        secondaryjoin="BotUser.id == AccountSession.bot_user_id",
        back_populates="accounts",
        viewonly=True,  # Делаем отношение read-only
        overlaps="sessions"  # Указываем конфликтующие отношения
    )


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.id", ondelete="CASCADE"), nullable=False
    )
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=True)
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)

    user = relationship("BotUser", back_populates="chats")
    dossiers = relationship("Dossier", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.id", ondelete="CASCADE"), nullable=False
    )
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")
    user = relationship("BotUser", back_populates="messages")


class Dossier(Base):
    __tablename__ = "dossiers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.id", ondelete="CASCADE"), nullable=False
    )
    target_user_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    summary_md: Mapped[str] = mapped_column(Text, nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("BotUser", back_populates="dossiers")
    chat = relationship("Chat", back_populates="dossiers")


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.id", ondelete="CASCADE"), nullable=False
    )
    openai_key: Mapped[str] = mapped_column(Text, nullable=True)
    llm_model: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("BotUser", back_populates="settings")


class Statistic(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)

    user = relationship("BotUser", back_populates="statistics")


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    service: Mapped[str] = mapped_column(Text, nullable=True)
    key: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.id", ondelete="CASCADE"), nullable=False
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    context_source: Mapped[str] = mapped_column(Text, nullable=True)
    context_size: Mapped[int] = mapped_column(Integer, nullable=True)
    response_text: Mapped[str] = mapped_column(Text, nullable=True)
    model_used: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("BotUser", back_populates="queries")
