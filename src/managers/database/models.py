from __future__ import annotations

from datetime import datetime
from typing import Any, Self, Type

from pytz import timezone
from sqlalchemy import Column, Integer, ScalarResult, select, String
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession

from src.managers.database import Base


def _current_timestamp():
    return datetime.now(timezone('Europe/Moscow')).strftime("%Y-%m-%d %H:%M:%S")


class GuildModel(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    guild_id = Column(String(22), unique=True, index=True, nullable=False)
    settings = Column(JSON, nullable=False, default={
        "language": "en-US",
        "mod": {
            "max_warns": 3,
            "punishment": "mute",
            "duration": "7d",
            "logs": None,
            "whitelist": {
                "roles": []
            },
        }, 
        "automod": {
            "punishment": "delete",
            "notify": None,
            "filters": {
                "symbols": False,
                "repeat": False,
                "mention": False,
                "invite": False,
                "media": False,
                "emoji": False,
                "regex": False
            },
            "limits": {
                "emoji": 5,
                "mentions": 5,
                "repeat": 3
            },
            "whitelist": {
                "roles": [],
                "channels": [],
                "links": []
            }, 
            "blacklist": {
                "links": []
            }
        }
    })
    
    @staticmethod
    async def fetch_one(session: AsyncSession, **kwargs: Any) -> GuildModel | None:
        result = await session.execute(select(GuildModel).filter_by(**kwargs))
        return result.scalar()

    @staticmethod
    async def fetch(session: AsyncSession, **kwargs: Any) -> ScalarResult[GuildModel]:
        result = await session.execute(select(GuildModel).filter_by(**kwargs))
        return result.scalars()

    def __str__(self) -> str:
        return f"guild_id={self.guild_id}, settings={self.settings}"


class AuditModel(Base):
    __tablename__ = "audit"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    action_type = Column(String(64), nullable=False)
    data = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, default=_current_timestamp())

    @staticmethod
    async def fetch_one(session: AsyncSession, **kwargs: Any) -> AuditModel | None:
        result = await session.execute(select(AuditModel).filter_by(**kwargs))
        return result.scalar()

    @staticmethod
    async def fetch(session: AsyncSession, **kwargs: Any) -> ScalarResult[AuditModel]:
        result = await session.execute(select(AuditModel).filter_by(**kwargs))
        return result.scalars()


class MemberModel(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    member_id = Column(String(22), unique=False, index=True, nullable=False)
    guild_id = Column(String(22), unique=False, index=True, nullable=False)
    balance = Column(Integer, default=0, nullable=False)
    card_balance = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    exp = Column(Integer, default=0, nullable=False)
    requires_exp = Column(Integer, default=100, nullable=False)
    voice_online = Column(Integer, default=0, nullable=False)
    msg_count = Column(Integer, default=0, nullable=False)

    @staticmethod
    async def fetch_one(session: AsyncSession, **kwargs: Any) -> MemberModel | None:
        result = await session.execute(select(MemberModel).filter_by(**kwargs))
        return result.scalar()

    @staticmethod
    async def fetch(session: AsyncSession, **kwargs: Any) -> ScalarResult[MemberModel]:
        result = await session.execute(select(MemberModel).filter_by(**kwargs))
        return result.scalars()

class BanModel(Base):
    __tablename__ = "tempbans"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    member_id = Column(String(22), unique=False, index=True, nullable=False)
    guild_id = Column(String(22), unique=False, index=True, nullable=False)
    until = Column(TIMESTAMP(timezone=False), nullable=True)
    ending = Column(TIMESTAMP(timezone=False), nullable=True)

    @staticmethod
    async def fetch_one(session: AsyncSession, **kwargs: Any) -> BanModel | None:
        result = await session.execute(select(BanModel).filter_by(**kwargs))
        return result.scalar()

    @staticmethod
    async def fetch(session: AsyncSession, **kwargs: Any) -> ScalarResult[BanModel]:
        result = await session.execute(select(BanModel).filter_by(**kwargs))
        return result.scalars()

class WarnModel(Base):
    __tablename__ = "warns"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    member_id = Column(String(22), unique=False, index=True, nullable=False)
    guild_id = Column(String(22), unique=False, index=True, nullable=False)
    executed_by = Column(String(22), unique=False, index=True, nullable=False)
    reason = Column(String(255), nullable=True, default=None)
    executed = Column(TIMESTAMP(timezone=False), nullable=True, default=_current_timestamp())
    expires = Column(TIMESTAMP(timezone=False), nullable=True)

    @staticmethod
    async def fetch_one(session: AsyncSession, **kwargs: Any) -> WarnModel | None:
        result = await session.execute(select(WarnModel).filter_by(**kwargs))
        return result.scalar()

    @staticmethod
    async def fetch(session: AsyncSession, **kwargs: Any) -> ScalarResult[WarnModel]:
        result = await session.execute(select(WarnModel).filter_by(**kwargs))
        return result.scalars()