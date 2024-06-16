import disnake
from disnake.ext import commands

from src.core import LocalLocalization

class selectModule(disnake.ui.StringSelect):
    def __init__(self, language):
        self.language = language
        
        localization = LocalLocalization()
        

        options = [
            disnake.SelectOption(
                label = f"{localization.format_string(self.language, 'Menu_AutoModTitle')}", description = f"{localization.format_string(self.language, 'Menu_AutoModDesc')}", emoji = "<:orpheus_automod:1188515335297577010>", value = "MenuAutoMod"
            ),
        ]

        super().__init__(
            placeholder = "",
            min_values = 1,
            max_values = 1,
            options = options
        )

class ModuleView(disnake.ui.View):
    def __init__(self, language):
        self.language = language 

        super().__init__()
        self.add_item(selectModule(self.language))