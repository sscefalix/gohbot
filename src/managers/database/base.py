from os import getenv

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = f"mysql+aiomysql://{getenv('DATABASE_USER')}:{getenv('DATABASE_PASSWORD')}@{getenv('DATABASE_HOST')}:{getenv('DATABASE_PORT')}/{getenv('DATABASE_NAME')}"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    ...
