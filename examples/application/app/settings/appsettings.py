from pathlib import Path

from PyQt5.QtCore import QSettings


class ApplicationSettings(QSettings):

    def __init__(self):

        path_settings = Path(__file__).parent.parent / "settings.ini"

        super().__init__(path_settings.absolute().as_posix(), QSettings.IniFormat)

    @property
    def data_folder_key(self) -> str:
        return "Paths/defaultDataPath"

    def get_data_folder(self) -> str:
        return self.value(self.data_folder_key, Path().expanduser().as_posix())
