from sqlalchemy.ext.asyncio import async_sessionmaker

from src.managers.database import Base, engine, SessionLocal


async def get_session() -> async_sessionmaker[SessionLocal]:
    async with engine.begin() as db:
        await db.run_sync(Base.metadata.create_all)

    session = SessionLocal
    return session
