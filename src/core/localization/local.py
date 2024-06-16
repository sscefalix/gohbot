from inspect import stack
from json import loads
from os import listdir
from os.path import exists
from typing import Any

from jinja2 import Template

from src.core.localization import LocalizationFolderNotFoundError


class LocalLocalization:
    def __new__(cls, *args, **kwargs) -> Any:
        instance = super(LocalLocalization, cls).__new__(cls)
        instance._path = stack()[1].filename  # Получаем путь к файлу, где создан класс

        return instance

    def __init__(self) -> None:
        self._data = self._init()

    @property
    def path(self) -> str:
        return self._path

    @staticmethod
    def _get_file_content(path: str) -> str:
        with open(path, encoding="utf-8") as file:
            return file.read()

    def _init(self) -> dict[str, dict[str, str]]:
        path = self.path.split("\\")
        category_path = "\\".join(path[:-2])

        if not exists(localization_path := f"{category_path}\\localization"):
            raise LocalizationFolderNotFoundError(folder="localization", path=category_path)

        if not exists(full_path := f"{localization_path}\\commands"):
            raise LocalizationFolderNotFoundError(folder="commands", path=localization_path)

        return {file_name.split(".")[0]: loads(file_content) for file_name, file_content in
                [(file, self._get_file_content(f"{full_path}\\{file}")) for file in listdir(full_path)]}

    def _get_string(self, language: str, key: str) -> str | None:
        return self._data.get(language, {}).get(key, None)

    def format_string(self, language: str, key: str, *, context: dict = None) -> str:
        if not context:
            context = {}

        template = Template(str(self._get_string(language=language, key=key)))
        return template.render(**context)
