import os
from os import PathLike


class DirectoryAlreadyExists(Exception):
    """Raises upon creation if directory already exists"""


class DirMaker:
    DEFAULT_DIRECTORY_NAME: PathLike | str = "New Directory"

    def __init__(self, directory: None | PathLike | str = None):
        match directory:
            case None:
                self.directory = self.DEFAULT_DIRECTORY_NAME
            case _:
                self.directory = directory

    def _is_exists(self) -> bool:
        return os.path.exists(self.directory)

    def create(self):
        if self._is_exists():
            raise DirectoryAlreadyExists()

        os.makedirs(self.directory)
