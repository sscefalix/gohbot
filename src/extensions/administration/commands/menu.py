import disnake
from disnake import CommandInteraction
from disnake.ext.commands import slash_command, guild_only

from src.core import Bot, LocalLocalization, Embed

from src.managers.database import get_session
from src.managers.database.models import GuildModel
from ..interactions.select_module import ModuleView

from typing import Any


@slash_command()
@guild_only()
async def menu_command(interaction: CommandInteraction) -> Any:
    """
    Menu command for setup bot without site {{MENU_COMMAND}}
    """
    async_session = await get_session()

    async with async_session() as session:
        async with session.begin():
            guild_model = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

    await session.close()

    localization = LocalLocalization()
    description = localization.format_string(str(guild_model.settings["language"]), "setupMenuDescription")

    embed = Embed(description=description)
    embed.set_author(name=localization.format_string(str(guild_model.settings["language"]), "setupMenuTitle"))

    return await interaction.response.send_message(embed=embed, view=ModuleView(str(guild_model.settings["language"])),
                                                   ephemeral=True)


def setup(bot: Bot) -> None:
    bot.add_slash_command(menu_command)
