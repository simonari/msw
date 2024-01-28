import os.path
from os import PathLike


class FileAlreadyExists(Exception):
    """Raises upon creation if file already exists"""


class FileMaker:
    DEFAULT_PATH: PathLike | str = "Simple file"

    def __init__(self, path: None | PathLike | str = None):
        self.path: PathLike | str

        match path:
            case None:
                self.path = self.DEFAULT_PATH
            case _:
                self.path = path

    def _is_exists(self) -> bool:
        return os.path.exists(self.path)

    def create(self):
        if self._is_exists():
            raise FileAlreadyExists()

        with open(self.path, "w"):
            pass
