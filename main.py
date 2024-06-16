from os import getenv

from disnake import Intents
from dotenv import load_dotenv

from src.core import Bot, I18N

load_dotenv()

bot = Bot(intents=Intents.all(), shard_count=1)

bot.load_extensions("src/extensions")
bot.load_events("src/listeners")

i18n = I18N("src/extensions", final_path="src/core/i18n")
i18n.start_script(
    file_names={
        "en": ("en-US.json", "en-GB.json"),
        "ru": ("ru.json",),
        "uk": ("uk.json",)
    }
)  # Запускаем скрипт для загрузки глобальной локализации I18N

bot.i18n.load("src/core/i18n")

bot.run(getenv("TOKEN"))
