from aiohttp.web_request import Request


class UserGuilds:
    @staticmethod
    async def get_user_guilds(request: Request, *args, **kwargs) -> tuple[list, int]:
        return ["a", "b"], 200
