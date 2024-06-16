from os import listdir

from disnake import Intents
from disnake.ext.commands import AutoShardedInteractionBot
from loguru import logger


class Bot(AutoShardedInteractionBot):
    def __init__(self, intents: Intents, *, shard_count: int | None = None) -> None:
        super().__init__(shard_count=shard_count, intents=intents)

    def load_extensions(self, path: str) -> None:
        for category in listdir(path):
            try:
                super().load_extensions(f"{path}\\{category}\\commands")
            except ValueError:
                logger.error(f"[BOT] Не удалось загрузить папку 'commands' по пути '{path}/{category}'")

            try:
                super().load_extensions(f"{path}\\{category}\\events")
            except ValueError:
                logger.error(f"[BOT] Не удалось загрузить папку 'events' по пути '{path}/{category}'")

    def load_events(self, path: str) -> None:
        super().load_extensions(path)
