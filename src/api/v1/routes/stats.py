from aiohttp.web_request import Request

from src.core import Bot


class Stats:
    @staticmethod
    async def get_stats(request: Request, *args, **kwargs) -> tuple[dict[str, str], int]:
        bot: Bot | None = kwargs.get("bot")

        return {
            "guilds": str(len(bot.guilds)),
            "users": str(len(list(bot.get_all_members())))
        }, 200

    @staticmethod
    async def get_top_guilds(request: Request, *args, **kwargs) -> tuple[list[dict[str, str]], int]:
        bot: Bot | None = kwargs.get("bot")

        guilds = [{"name": g.name, "member_count": str(g.member_count)} for g in bot.guilds]
        sorted_guilds = sorted(guilds, key=lambda i: int(i["member_count"]), reverse=True)

        return sorted_guilds, 200

    @staticmethod
    async def get_status(request: Request, *args, **kwargs) -> tuple[dict[str, str | list[dict[str, str]]], int]:
        bot: Bot | None = kwargs.get("bot")

        shards = [{"id": str(s), "latency": f"{bot.get_shard(s).latency * 1000:.2f}"} for s in bot.shards]

        return {
            "latency": f"{bot.latency * 1000:.2f}",
            "shards": shards
        }, 200
