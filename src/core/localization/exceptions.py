class LocalizationFolderNotFoundError(BaseException):
    def __init__(self, *args, folder: str, path: str, **kwargs):
        super().__init__(f"Не удалось найти папку '{folder}' по пути '{path}'")
