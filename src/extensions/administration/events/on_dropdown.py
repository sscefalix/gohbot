import disnake
from typing import Any, Callable, Coroutine

from src.api.v1 import App
from src.core import Bot, Embed, LocalLocalization
from src.managers.database import get_session
from typing import List
from sqlalchemy import update
from src.managers.database.models import GuildModel, MemberModel
from loguru import logger

from ..interactions.paginator import Paginator

async def on_dropdown_menu(interaction: disnake.Interaction) -> Callable[[], Coroutine[Any, Any, Any]]:
    
    async_session = await get_session()

    async with async_session() as session:
        async with session.begin():
            guildModel = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

    await session.close()

    localization = LocalLocalization()
    bot = interaction.bot


    if interaction.values[0] == "MenuAutoMod":  
        embed = Embed(
            description = localization.format_string(str(guildModel.settings['language']), "AutoModGuideDesc")
        )
        embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModGuideTitle"))
        
        
        row = disnake.ui.ActionRow()
        row.add_button(label = localization.format_string(str(guildModel.settings['language']), "AutoModFilters"), style=disnake.ButtonStyle.grey, custom_id="AutoModFilters", emoji="<:orpheus_analytics:1188537080066883775>")
        row.add_button(label = localization.format_string(str(guildModel.settings['language']), "AutoModPunishment"), style=disnake.ButtonStyle.grey, custom_id="AutoModPunishment", emoji="<:orpheus_punishment:1188537076002594918>")
        row.add_button(label = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"), style=disnake.ButtonStyle.grey, custom_id="AutoModWhitelist", emoji="<:orpheus_whitelist:1188537395486928958>")
        row.add_button(label = localization.format_string(str(guildModel.settings['language']), "AutoModNotify"), style=disnake.ButtonStyle.grey, custom_id="AutoModNotify", emoji="<:orpheus_notify:1188537392336994396>") 
       
        await interaction.response.edit_message(embed=embed, components=[row])

    if interaction.data.custom_id == "selectNotifyDropdown":
        row = disnake.ui.ActionRow()
        row.add_button(
            emoji = "🔙",
            style = disnake.ButtonStyle.danger,
            custom_id = "AutoModMainBack"
        )

        try:
            channel = await bot.fetch_channel(interaction.values[0])
        except:
            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModNotifyErr"))
            embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModNotify"))

            return await interaction.response.edit_message(embed=embed, components=[row])    

        if type(channel) is disnake.TextChannel:

            async_session = await get_session()

            async with async_session() as session:
                async with session.begin():
                    guild_model = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

                    guild_settings = dict(guildModel.settings)
                    guild_settings["automod"]["notify"] = str(interaction.values[0])
    
                    query = update(GuildModel).where(GuildModel.guild_id == guild_model.guild_id).values(settings = guild_settings)
                    await session.execute(query) 
                    await session.commit()
                    await session.close()

            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModNotifySucc"))
            embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModNotify"))
        
            return await interaction.response.edit_message(embed=embed, components=[row]) 
        
        embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModNotifyErr"))
        embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModNotify"))

        return await interaction.response.edit_message(embed=embed, components=[row])    
        
    if interaction.data.custom_id == "AutoModWhitelist_AddChannel":
        row = disnake.ui.ActionRow()
        row.add_button(
            emoji = "🔙",
            style = disnake.ButtonStyle.danger,
            custom_id = "AutoModMainBack"
        )

        try:
            channel = await bot.fetch_channel(interaction.values[0])
        except:
            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_ChannelErr"))
            embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

            return await interaction.response.edit_message(embed=embed, components=[row])    

        if type(channel) is disnake.TextChannel:

            guild_settings = dict(guildModel.settings)
            currentList = guild_settings['automod']['whitelist']['channels']

            if channel.id in currentList:
                embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_ChannelAddExist"))
                embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

                return await interaction.response.edit_message(embed=embed, components=[row])

            async_session = await get_session()

            async with async_session() as session:
                async with session.begin():
                    guildModel = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

                    guild_settings = dict(guildModel.settings)
                    currentList.append(channel.id)
                    guild_settings["automod"]["whitelist"]["channels"] = currentList
    
                    query = update(GuildModel).where(GuildModel.guild_id == guildModel.guild_id).values(settings = guild_settings)
                    await session.execute(query) 
                    await session.commit()
                    await session.close()

            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_ChannelAddSucc"))
            embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

            return await interaction.response.edit_message(embed=embed, components=[row])

        embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_ChannelErr"))
        embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

        return await interaction.response.edit_message(embed=embed, components=[row])  
    if interaction.data.custom_id == "AutoModWhitelist_AddRole":
        row = disnake.ui.ActionRow()
        row.add_button(
            emoji = "🔙",
            style = disnake.ButtonStyle.danger,
            custom_id = "AutoModMainBack"
        )

        try:
            role = disnake.utils.get(interaction.guild.roles, id = int(interaction.values[0]))
        except Exception as e:
            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_RoleErr"))
            embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

            return await interaction.response.edit_message(embed=embed, components=[row])    
        
        if type(role) is disnake.Role:

            guild_settings = dict(guildModel.settings)
            currentList = guild_settings['automod']['whitelist']['roles']

            if role.id in currentList:
                embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_RoleAddExist"))
                embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

                return await interaction.response.edit_message(embed=embed, components=[row])

            async_session = await get_session()

            async with async_session() as session:
                async with session.begin():
                    guildModel = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

                    guild_settings = dict(guildModel.settings)
                    currentList.append(role.id)
                    guild_settings["automod"]["whitelist"]["roles"] = currentList
    
                    query = update(GuildModel).where(GuildModel.guild_id == guildModel.guild_id).values(settings = guild_settings)
                    await session.execute(query) 
                    await session.commit()
                    await session.close()

            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_RoleAddSucc"))
            embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

            return await interaction.response.edit_message(embed=embed, components=[row])   

        embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_RoleErr"))
        embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

        return await interaction.response.edit_message(embed=embed, components=[row])   

    if interaction.data.custom_id == "AutoModWhitelist_RemoveChannel":
        row = disnake.ui.ActionRow()
        row.add_button(
            emoji = "🔙",
            style = disnake.ButtonStyle.danger,
            custom_id = "AutoModMainBack"
        )

        try:
            channel = await bot.fetch_channel(interaction.values[0])
        except:
            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_ChannelErr"))
            embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

            return await interaction.response.edit_message(embed=embed, components=[row])    

        if type(channel) is disnake.TextChannel:

            guild_settings = dict(guildModel.settings)
            currentList = guild_settings['automod']['whitelist']['channels']

            if not channel.id in currentList:
                embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_ChannelRemoveExist"))
                embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

                return await interaction.response.edit_message(embed=embed, components=[row])

            async_session = await get_session()

            async with async_session() as session:
                async with session.begin():
                    guildModel = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

                    guild_settings = dict(guildModel.settings)
                    currentList.remove(channel.id)
                    guild_settings["automod"]["whitelist"]["channels"] = currentList
    
                    query = update(GuildModel).where(GuildModel.guild_id == guildModel.guild_id).values(settings = guild_settings)
                    await session.execute(query) 
                    await session.commit()
                    await session.close()

            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_ChannelRemoveSucc"))
            embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

            return await interaction.response.edit_message(embed=embed, components=[row])

    if interaction.data.custom_id == "AutoModWhitelist_RemoveRole":
        row = disnake.ui.ActionRow()
        row.add_button(
            emoji = "🔙",
            style = disnake.ButtonStyle.danger,
            custom_id = "AutoModMainBack"
        )

        try:
            role = disnake.utils.get(interaction.guild.roles, id = int(interaction.values[0]))
        except:
            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_RoleErr"))
            embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

            return await interaction.response.edit_message(embed=embed, components=[row])    

        if type(role) is disnake.Role:

            guild_settings = dict(guildModel.settings)
            currentList = guild_settings['automod']['whitelist']['roles']

            if not role.id in currentList:
                embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_RoleRemoveExist"))
                embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

                return await interaction.response.edit_message(embed=embed, components=[row])

            async_session = await get_session()

            async with async_session() as session:
                async with session.begin():
                    guildModel = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

                    guild_settings = dict(guildModel.settings)
                    currentList.remove(role.id)
                    guild_settings["automod"]["whitelist"]["roles"] = currentList
    
                    query = update(GuildModel).where(GuildModel.guild_id == guildModel.guild_id).values(settings = guild_settings)
                    await session.execute(query) 
                    await session.commit()
                    await session.close()

            embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_RoleRemoveSucc"))
            embed.set_author(name = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

            return await interaction.response.edit_message(embed=embed, components=[row])   

        embed = Embed(description = localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist_RoleErr"))
        embed.set_author(name=localization.format_string(str(guildModel.settings['language']), "AutoModWhitelist"))

        return await interaction.response.edit_message(embed=embed, components=[row])   

def setup(bot: Bot) -> None:
    bot.add_listener(on_dropdown_menu, "on_dropdown")
