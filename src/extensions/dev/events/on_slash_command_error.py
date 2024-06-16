from disnake import ApplicationCommandInteraction
from loguru import logger

from src.core import Bot, Embed, LocalLocalization
from src.managers.database import get_session
from src.managers.database.models import GuildModel, MemberModel


async def on_slash_command_error_event(inter: ApplicationCommandInteraction, error) -> None:
    try:
        localization = LocalLocalization()
        async_session = await get_session()

        async with async_session() as session:
            async with session.begin():
                guildModel = await GuildModel.fetch_one(session, guild_id=str(inter.guild.id))
        
        await session.close()

        description = localization.format_string(str(guildModel.settings['language']), "SlashErrorDesc")

        embed = Embed(description=description)
        embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "SlashErrorTitle"))

        return await inter.response.send_message(embed=embed, ephemeral=True)
    except:
        pass 

def setup(bot: Bot) -> None:
    bot.add_listener(on_slash_command_error_event, "on_slash_command_error")
