from typing import Self

from loguru import logger
from redis.asyncio import StrictRedis


class AsyncCache:
    __instance: Self | None = None

    def __init__(self, host: str, port: int, db: int, password: str, debug: bool = True) -> None:
        self._redis = StrictRedis(host=host, port=port, db=db, password=password)
        self._debug = debug

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __del__(self) -> None:
        self.__instance = None

    async def _set(self, key: bytes | str, value: bytes | str | int | float, expires_at: int | None = None) -> bool:
        return await self._redis.set(name=key, value=value, ex=expires_at)

    async def set(self, key: bytes | str, value: bytes | str | int | float, expires_at: int | None = None) -> bool:
        if not expires_at:
            expires_at = -1

        if await self.get(key=key):
            if self._debug:
                logger.success(
                    f"[CACHE] Данные по ключу '{key}' не были обновлены, так как они уже были кешированы и используется метод 'set'."
                )

        else:
            logger.success(f"[CACHE] Данные сохранены в кеш по ключу: '{key}'.")

            return await self._set(key=key, value=value, expires_at=expires_at)

    async def get(self, key: bytes | str) -> str | int | float | None:
        cache: bytes | None = await self._redis.get(name=key)

        if self._debug:
            logger.success(f"[CACHE] Данные получены из кеша по ключу: '{key}'")

        if cache:
            return cache.decode()

    async def update(self, key: bytes | str, value: bytes | str | int | float, expires_at: int | None = None) -> bool:
        logger.success(f"[CACHE] Данные по ключу '{key}' были обновлены.")

        return await self._set(key=key, value=value, expires_at=expires_at)
