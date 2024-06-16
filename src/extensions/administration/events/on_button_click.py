import disnake
from typing import Any, Callable, Coroutine

from disnake.ui import ActionRow, Button, RoleSelect

from src.core import Bot, Embed, LocalLocalization
from src.managers.database import get_session
from sqlalchemy import update
from src.managers.database.models import GuildModel

from ..interactions.paginator import Paginator


async def on_button_click(interaction: disnake.Interaction) -> Callable[[], Coroutine[Any, Any, Any]]:
    async_session = await get_session()

    async with async_session() as session:
        async with session.begin():
            guild_model = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

    await session.close()

    localization = LocalLocalization()
    language = str(guild_model.settings["language"])
    punishment_type = guild_model.settings["automod"]["punishment"]

    row = ActionRow()
    embed = Embed()

    async def main_btn_update():
        embed.description = localization.format_string(str(guild_model.settings["language"]), "AutoModGuideDesc")
        embed.set_author(name=localization.format_string(str(guild_model.settings["language"]), "AutoModGuideTitle"))

        row.append_item(
            Button(label=localization.format_string(str(guild_model.settings["language"]), "AutoModFilters"),
                   style=disnake.ButtonStyle.grey, custom_id="AutoModFilters",
                   emoji="<:orpheus_analytics:1188537080066883775>"))
        row.append_item(
            Button(label=localization.format_string(str(guild_model.settings["language"]), "AutoModPunishment"),
                   style=disnake.ButtonStyle.grey, custom_id="AutoModPunishment",
                   emoji="<:orpheus_punishment:1188537076002594918>"))
        row.append_item(
            Button(label=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist"),
                   style=disnake.ButtonStyle.grey, custom_id="AutoModWhitelist",
                   emoji="<:orpheus_whitelist:1188537395486928958>"))
        row.append_item(Button(label=localization.format_string(str(guild_model.settings["language"]), "AutoModNotify"),
                               style=disnake.ButtonStyle.grey, custom_id="AutoModNotify",
                               emoji="<:orpheus_notify:1188537392336994396>"))

        await interaction.response.edit_message(embed=embed, components=[row])

    async def filters_btn_update():
        nonlocal row
        nonlocal embed

        rows = []

        filter_settings = [
            ("Symbols", "AutoModSymbols"),
            ("Repeat", "AutoModRepeat"),
            ("Mention", "AutoModMention"),
            ("Invite", "AutoModInvite"),
            ("Media", "AutoModMedia"),
            ("Emoji", "AutoModEmoji"),
        ]

        row.append_item(Button(
            emoji="🔙",
            style=disnake.ButtonStyle.danger,
            custom_id="AutoModMainBack",
            row=1
        ))

        for filter_name, custom_id in filter_settings:
            if len(row.children) >= 5:
                rows.append(row)
                row = disnake.ui.ActionRow()

            is_filter_enabled = guild_model.settings["automod"]["filters"][filter_name.lower()]
            button_style = disnake.ButtonStyle.green if is_filter_enabled else disnake.ButtonStyle.danger

            row.append_item(Button(
                label=localization.format_string(language, f"AutoModFilter_{filter_name}Title"),
                style=button_style,
                custom_id=custom_id,
                row=1
            ))

        rows.append(row)

        embed.description = localization.format_string(str(guild_model.settings["language"]), "AutoModFiltersDesc")
        embed.set_author(name=localization.format_string(str(guild_model.settings["language"]), "AutoModFilters"))
        embed.set_footer(text=localization.format_string(str(guild_model.settings["language"]), "AutoModFiltersFooter"))

        await interaction.response.edit_message(embed=embed, components=rows)

    async def punishment_btn_update():
        nonlocal row

        row.clear_items()

        punishment_strings = {
            "delete": localization.format_string(str(guild_model.settings["language"]),
                                                 "AutoModPunishment_DeleteTitle"),
            "warn": localization.format_string(str(guild_model.settings["language"]), "AutoModPunishment_WarnTitle"),
            "kick": localization.format_string(str(guild_model.settings["language"]), "AutoModPunishment_KickTitle"),
            "ban": localization.format_string(str(guild_model.settings["language"]), "AutoModPunishment_BanTitle")
        }

        row.append_item(Button(
            emoji="🔙",
            style=disnake.ButtonStyle.danger,
            custom_id="AutoModMainBack",
            row=1
        ))
        row.append_item(Button(
            label=f"{localization.format_string(str(guild_model.settings['language']), key='AutoModPunishment_CurrentTitle')}{punishment_strings.get(punishment_type, '')}",
            style=disnake.ButtonStyle.grey,
            disabled=True,
            emoji="<:orpheus_danger:1188864273670230048>"
        ))

        for option in punishment_strings:
            row.append_item(Button(
                label=punishment_strings[option],
                style=disnake.ButtonStyle.green if punishment_type == option else disnake.ButtonStyle.gray,
                custom_id=f"AutoModPunishment_{option.capitalize()}",
                disabled=True if punishment_type == option else False,
                row=2
            ))

        embed.description = localization.format_string(str(guild_model.settings["language"]), "AutoModPunishmentDesc")
        embed.set_author(name=localization.format_string(str(guild_model.settings["language"]), "AutoModPunishment"))

        await interaction.response.edit_message(embed=embed, components=[row])

    async def whitelist_btn_update():
        nonlocal row
        nonlocal embed

        row.append_item(Button(
            emoji="🔙",
            style=disnake.ButtonStyle.danger,
            custom_id="AutoModMainBack"
        ))

        row.append_item(Button(
            label=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist_Add"),
            style=disnake.ButtonStyle.green,
            custom_id=f"AutoModWhitelist_Add"
        ))

        row.append_item(Button(
            label=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist_Remove"),
            style=disnake.ButtonStyle.danger,
            custom_id=f"AutoModWhitelist_Remove"
        ))

        row.append_item(Button(
            label=localization.format_string(str(guild_model.settings["language"]),
                                             "AutoModWhitelist_ChannelListTitle"),
            style=disnake.ButtonStyle.grey,
            custom_id=f"AutoModWhitelist_ChannelList"
        ))

        row.append_item(Button(
            label=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist_RoleListTitle"),
            style=disnake.ButtonStyle.grey,
            custom_id=f"AutoModWhitelist_RoleList"
        ))

        embed.description = localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelistDesc")
        embed.set_author(name=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist"))

        await interaction.response.edit_message(embed=embed, components=[row])

        def notify_btn_update():
            nonlocal embed
            nonlocal row

            row.clear_items()

            embed.description = localization.format_string(str(guild_model.settings["language"]), "AutoModNotifyDesc")
            embed.set_author(name=localization.format_string(str(guild_model.settings["language"]), "AutoModNotify"))

            row.append_item(Button(
                emoji="🔙",
                style=disnake.ButtonStyle.danger,
                custom_id="AutoModMainBack"
            ))

            row2.add_channel_select(
                custom_id="selectNotifyDropdown",
                min_values=1,
                max_values=1
            )

            await interaction.response.edit_message(embed=embed, components=[row])

            def update_punishment_settings(interaction, punishment_type):
                async_session = await get_session()

                async with async_session() as session:
                    async with session.begin():
                        guild_model = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

                        guild_settings = dict(guild_model.settings)
                        guild_settings["automod"]["punishment"] = punishment_type

                        query = update(GuildModel).where(GuildModel.guild_id == guild_model.guild_id).values(
                            settings=guild_settings)
                        await session.execute(query)
                        await session.commit()
                        await session.close()

                embed = Embed(
                    description=localization.format_string(str(guild_model.settings["language"]),
                                                           "AutoModPunishmentSucc"))
                embed.set_author(
                    name=localization.format_string(str(guild_model.settings["language"]), "AutoModPunishment"))

                await punishment_btn_update()

            update_functions = {
                "AutoModFilters": filters_btn_update,
                "AutoModPunishment": punishment_btn_update,
                "AutoModWhitelist": whitelist_btn_update,
                "AutoModNotify": notify_btn_update,
            }

            filter_types = ["symbols", "repeat", "mention", "links", "invite", "media", "emoji"]

            async def update_filter_settings(interaction, filter_type):
                async_session = await get_session()

                async with async_session() as session:
                    async with session.begin():
                        guild_model = await GuildModel.fetch_one(session, guild_id=str(interaction.guild.id))

                        guild_settings = dict(guild_model.settings)
                        guild_settings["automod"]["filters"][filter_type] = not guild_settings["automod"]["filters"][
                            filter_type]

                        query = update(GuildModel).where(GuildModel.guild_id == guild_model.guild_id).values(
                            settings=guild_settings)
                        await session.execute(query)
                        await session.commit()
                        await session.close()

                await filters_btn_update()

            for filter_type in filter_types:
                if interaction.component.custom_id == f"AutoMod{filter_type.capitalize()}":
                    print(filter_type)
                    await update_filter_settings(interaction, filter_type)

            if interaction.component.custom_id in update_functions:
                await update_functions[interaction.component.custom_id]()

            if interaction.component.custom_id.startswith("AutoModPunishment_"):
                punishment_type_ = interaction.component.custom_id.replace("AutoModPunishment_", "").lower()
                await update_punishment_settings(interaction, punishment_type_)

            if interaction.component.custom_id == "AutoModMainBack":
                await main_btn_update()

            if interaction.component.custom_id == "AutoModWhitelist_Add":
                row.append_item(Button(
                    emoji="🔙",
                    style=disnake.ButtonStyle.danger,
                    custom_id="AutoModMainBack",
                    row=1
                ))

                row.add_item(RoleSelect(
                    custom_id="AutoModWhitelist_AddRole",
                    min_values=1,
                    max_values=1,
                    row=2
                ))

                row3 = disnake.ui.ActionRow()
                row3.add_channel_select(
                    custom_id="AutoModWhitelist_AddChannel",
                    min_values=1,
                    max_values=1
                )

                embed = Embed(
                    description=localization.format_string(str(guild_model.settings["language"]),
                                                           "AutoModWhitelist_AddDesc"))
                embed.set_author(
                    name=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist"))

                await interaction.response.edit_message(embed=embed, components=[row, row2, row3])

            if interaction.component.custom_id == "AutoModWhitelist_Remove":
                row = disnake.ui.ActionRow()
                row.append_item(Button(
                    emoji="🔙",
                    style=disnake.ButtonStyle.danger,
                    custom_id="AutoModMainBack"
                )

                row2 = disnake.ui.ActionRow()
                row2.add_role_select(
                    custom_id="AutoModWhitelist_RemoveRole",
                    min_values=1,
                    max_values=1
                )

                row3 = disnake.ui.ActionRow()
                row3.add_channel_select(
                    custom_id="AutoModWhitelist_RemoveChannel",
                    min_values=1,
                    max_values=1
                )

                embed = Embed(
                    description=localization.format_string(str(guild_model.settings["language"]),
                                                           "AutoModWhitelist_RemoveDesc"))
                embed.set_author(
                    name=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist"))

                await interaction.response.edit_message(embed=embed, components=[row, row2, row3])

                if interaction.component.custom_id == "AutoModWhitelist_ChannelList":
                    channelList = guild_model.settings["automod"]["whitelist"]["channels"]

                row = disnake.ui.ActionRow()
                row.append_item(Button(
                    emoji="🔙",
                    style=disnake.ButtonStyle.danger,
                    custom_id="AutoModMainBack"
                )

                if len(channelList) <= 0:
                    embed = Embed(description=localization.format_string(str(guild_model.settings["language"]),
                                                                         "AutoModWhitelist_ChannelsEmpty"))
                embed.set_author(
                    name=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist"))
                return await interaction.response.edit_message(embed=embed, components=[row])

                embeds = []

                for i in range(0, len(channelList), 10):
                    chunk = channelList[i:i + 10]
                    embed = Embed(
                        description=localization.format_string(str(guild_model.settings["language"]),
                                                               "AutoModWhitelist_ChannelListDesc")
                    )
                    embed.add_field(
                        name="\n",
                        value="\n".join([f"{index}. <#{obj}>" for index, obj in enumerate(chunk, start=1)]),
                        inline=False
                    )
                    embed.set_author(name=localization.format_string(str(guild_model.settings["language"]),
                                                                     "AutoModWhitelist_ChannelListTitle"))
                    embeds.append(embed)

                await interaction.response.edit_message(embed=embeds[0], view=Paginator(embeds))

            if interaction.component.custom_id == "AutoModWhitelist_RoleList":
                rolesList = guild_model.settings["automod"]["whitelist"]["roles"]

                row = disnake.ui.ActionRow()
                row.append_item(Button(
                    emoji="🔙",
                    style=disnake.ButtonStyle.danger,
                    custom_id="AutoModMainBack"
                )

                if len(rolesList) <= 0:
                    embed = Embed(description=localization.format_string(str(guild_model.settings["language"]),
                                                                         "AutoModWhitelist_RoleEmpty"))
                embed.set_author(
                    name=localization.format_string(str(guild_model.settings["language"]), "AutoModWhitelist"))
                return await interaction.response.edit_message(embed=embed, components=[row])

                embeds = []

                for i in range(0, len(rolesList), 10):
                    chunk = rolesList[i:i + 10]
                    embed = Embed(
                        description=localization.format_string(str(guild_model.settings["language"]),
                                                               "AutoModWhitelist_ChannelListDesc")
                    )
                    embed.add_field(
                        name="\n",
                        value="\n".join([f"{index}. <@&{obj}>" for index, obj in enumerate(chunk, start=1)]),
                        inline=False
                    )
                    embed.set_author(name=localization.format_string(str(guild_model.settings["language"]),
                                                                     "AutoModWhitelist_ChannelListTitle"))
                    embeds.append(embed)

                await interaction.response.edit_message(embed=embeds[0], view=Paginator(embeds))

        def setup(bot: Bot) -> None:
            bot.add_listener(on_button_click, "on_button_click")
