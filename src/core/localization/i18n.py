from json import dump, loads
from os import listdir
from os.path import exists, isdir

from src.core.localization import LocalizationFolderNotFoundError


class I18N:
    def __init__(self, extensions_path: str, final_path: str) -> None:
        self._path = extensions_path
        self._final = final_path
        self._data = self._init()

    @property
    def path(self):
        return self._path

    @property
    def final_path(self):
        return self._final

    @staticmethod
    def _get_file_content(path: str) -> str:
        with open(path, encoding="utf-8") as file:
            return file.read()

    def _init(self) -> dict[str, dict[str, str]]:
        content = {}

        for category in listdir(self.path):  # Проходимся по каждой категории
            if not exists(
                full_path := f"{self.path}\\{category}\\localization"
            ):  # Если в папке категории нет папки localization, то выдаём ошибку
                raise LocalizationFolderNotFoundError(folder="localization", path=f"{self.path}\\{category}")

            data = {file_name.split(".")[0]: loads(file_content) for file_name, file_content in
                    [(file, self._get_file_content(f"{full_path}\\{file}")) for file in listdir(full_path) if
                     not isdir(
                         f"{full_path}\\{file}"
                     )]}  # Конвертируем все файлы в вид {"file_name": dict[<content[str]>]}

            for file_name, file_content in data.items():
                if file_name not in content:
                    content[file_name] = {}

                content[file_name] = content[file_name] | file_content

        return content

    def start_script(self, *, file_names: dict[str, tuple[str]]) -> None:
        for name, content in self._data.items():
            for file_name in file_names[name]:
                with open(f"{self.final_path}\\{file_name}", "w", encoding="utf-8") as file:
                    dump(content, file, sort_keys=True, ensure_ascii=True, indent=2)
