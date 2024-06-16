from disnake import Guild
from loguru import logger

from src.core import Bot
from src.managers.database import get_session
from src.managers.database.models import GuildModel, MemberModel


async def on_guild_join_event(guild: Guild) -> None:
    async_session = await get_session()

    async with async_session() as session:
        async with session.begin():

            if not (await GuildModel.fetch_one(session, guild_id=str(guild.id))):
                record = GuildModel(guild_id=str(guild.id))
                session.add(record)
                logger.success(f"[MySQL] Создана новая запись GuildModel: {record}")

            await session.commit()
            await session.close()

    logger.success(f"[BOT] Добавлен на новый сервер: {guild.name}({guild.id})")


def setup(bot: Bot) -> None:
    bot.add_listener(on_guild_join_event, "on_guild_join")
