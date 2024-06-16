from disnake import ApplicationCommandInteraction
from loguru import logger

from src.core import Bot
from src.managers.database import get_session
from src.managers.database.models import GuildModel, MemberModel


async def on_slash_command_event(inter: ApplicationCommandInteraction) -> None:
    async_session = await get_session()

    async with async_session() as session:
        async with session.begin():

            if not (await GuildModel.fetch_one(session, guild_id=str(inter.guild.id))):
                record = GuildModel(guild_id=str(inter.guild.id))
                session.add(record)
                logger.success(f"[MySQL] Создана новая запись GuildModel: {record}")

            if not inter.author.bot:
                if not (await MemberModel.fetch_one(session, member_id=str(inter.author.id), guild_id=str(inter.guild.id))):
                    record = MemberModel(
                        member_id=str(inter.author.id),
                        guild_id=str(inter.guild.id)
                    )
                    session.add(record)
                    logger.info(f"[MySQL] Создана новая запись MemberModel: {record}")

            await session.commit()
            await session.close()


def setup(bot: Bot) -> None:
    bot.add_listener(on_slash_command_event, "on_slash_command")
