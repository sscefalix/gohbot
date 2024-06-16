from importlib import import_module
from os import getenv, listdir
from pathlib import Path
from sys import argv
from typing import Any, Callable

from aiohttp.web import Application, json_response, Request, Response
from aiohttp.web_runner import AppRunner, TCPSite
from dotenv import load_dotenv
from loguru import logger

from src.core import Bot

load_dotenv()


class App:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._app = Application()

    @staticmethod
    def _json_response(data: dict[str, Any] | list[Any], status: int) -> Response:
        return json_response(data=data, content_type="application/json", status=status)

    def _get_handler(self, handler: Callable) -> Callable:
        async def get_handler_helper(request: Request) -> Response:
            handled = await handler(request, bot=self._bot)  # Вызываем хендлер и передаем параметры запроса и бота
            return self._json_response(*handled)

        return get_handler_helper

    def _load_routes(self) -> None:
        routes = {}

        app_path: str = str(Path(__file__).parent)  # Получаем путь к текущему файлу (app.py)
        root_path: str = str(Path(argv[0]).parent)  # Получаем путь файла запуска бота
        import_path: str = ".".join(
            app_path.split("\\")[len(root_path.split("\\")):]
        )  # Получаем путь для импорта

        for route in listdir(f"{app_path}\\routes"):
            if route.startswith("__"):
                continue

            route: str = ".".join(route.split(".")[0:-1])  # Обрезаем расширение файла
            route_module = import_module(f"{import_path}.routes.{route}")  # Импортируем модуль файла

            try:
                route_class = getattr(
                    route_module, "".join(route.replace("_", " ").title().split())
                )  # Получаем класс по имени файла конвертируя example_one в ExampleOne

                methods = [method for method in dir(route_class) if
                           callable(getattr(route_class, method)) and method.startswith(
                               ("get", "post", "put", "delete")
                           )]  # Получаем все методы класса, которые присутствуют в http методах get, post, put, delete

                for method in methods:
                    http_method, *route = method.split(
                        "_"
                    )  # Получаем http метод классового метода, и остальное название функции без http метода
                    path = "/".join(route)  # Получаем http маршрут

                    routes[f"/{path}"] = {
                        "http_method": http_method,
                        "handler": getattr(route_class, method)
                    }
            except AttributeError:
                logger.warning(f"[API] Не удалось загрузить класс из файла '{route}.py'.")

        for path, data in routes.items():
            self._app.router.add_route(
                method=data["http_method"], path=path, handler=self._get_handler(handler=data["handler"])
            )  # Добавляем метод в aiohttp router

            logger.success(f"[API] Добавлен метод ({str(data['http_method']).upper()}) {path}")

    async def run(self) -> None:
        self._load_routes()  # Загружаем роуты

        runner = AppRunner(app=self._app)
        await runner.setup()

        tcp = TCPSite(runner=runner, host=getenv("API_HOST"), port=int(getenv("API_PORT")))
        await tcp.start()

        logger.success(f"[API] Запущено на порту {getenv('API_PORT')} ({getenv('API_HOST')}:{getenv('API_PORT')})")
