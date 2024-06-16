from typing import Any, Callable, Coroutine

from src.api.v1 import App
from src.core import Bot
from src.managers.database import get_session
from src.managers.database.models import GuildModel, MemberModel
from loguru import logger


def get_on_ready_event(bot: Bot) -> Callable[[], Coroutine[Any, Any, Any]]:
    async def _create_database_guild_records() -> None:
        async_session = await get_session()

        async with async_session() as session:
            async with session.begin():

                for guild in bot.guilds:
                    if not (await GuildModel.fetch_one(session, guild_id=str(guild.id))):
                        record = GuildModel(guild_id=str(guild.id))
                        session.add(record)
                        logger.info(f"[MySQL] Создана новая запись GuildModel: {record}")

                await session.commit()
                await session.close()

    async def _run_web_server() -> None:
        web_server = App(bot=bot)
        await web_server.run()

    async def _ready_event() -> None:
        await _create_database_guild_records()
        # await _run_web_server()

        logger.success("[BOT] Запущен!")

    return _ready_event


def setup(bot: Bot) -> None:
    bot.add_listener(func=get_on_ready_event(bot=bot), name="on_ready")
