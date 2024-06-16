from typing import List

from disnake import ButtonStyle, MessageInteraction
from disnake.ui import View, Button, button

from src.core import Embed


class Paginator(View):
    def __init__(self, embeds: List[Embed]):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.index = 0

        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"{i + 1} / {len(self.embeds)}")

        self._update_state()

    def _update_state(self) -> None:
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1

    @button(emoji="⏪", style=ButtonStyle.blurple)
    async def first_page(self, _button: Button, inter: MessageInteraction):
        self.index = 0

        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @button(emoji="◀", style=ButtonStyle.secondary)
    async def prev_page(self, _button: Button, inter: MessageInteraction):
        self.index -= 1

        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @button(emoji="🗑️", style=ButtonStyle.red)
    async def remove(self, _button: Button, inter: MessageInteraction):
        await inter.response.edit_message(view=None)

    @button(emoji="▶", style=ButtonStyle.secondary)
    async def next_page(self, _button: Button, inter: MessageInteraction):
        self.index += 1

        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @button(emoji="⏩", style=ButtonStyle.blurple)
    async def last_page(self, _button: Button, inter: MessageInteraction):
        self.index = len(self.embeds) - 1

        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)
