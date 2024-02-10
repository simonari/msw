import os
import json
from datetime import datetime
from .DirMaker import DirMaker, DirectoryAlreadyExists
from .FileMaker import FileMaker, FileAlreadyExists

Entry = dict[str, str]
Path = str | os.PathLike


class TimetableEmptyFormat(ValueError):
    """No timetable format provided"""


class TimetableUnexpectedFormat(ValueError):
    """Not supported timetable format provided"""


class TimetableEntryMissingTime(ValueError):
    """No time provided in entry"""


class TimetableEntryWrongTimeFormat(ValueError):
    """Wrong time format"""


class BaseTimetableFile:
    DEFAULT_PATH: Path = ".timetables/timetable"

    def __init__(self, path: Path | None = None):
        self._dir: Path
        self._filename: str
        self._ext: str
        self._local: bool

        if path is None:
            path = self.DEFAULT_PATH

        self._path: Path = path

        self._parse_path(path)
        self._setup()

    def _parse_path(self, path: Path):
        self._dir, self._filename = os.path.split(path)
        self._validate_dir_and_filename()
        _, self._ext = os.path.splitext(self._filename)

    def _is_file_local(self) -> bool:
        if self._dir == "" and self._filename is not None:
            self._dir = os.getcwd()
            return True

        return False

    def _validate_dir_and_filename(self):
        self._local = self._is_file_local()
        if not self._local and self._filename is None:
            # TODO: implement error
            raise NotImplementedError

    def _make_dir(self):
        if self._local:
            return

        dir_maker = DirMaker(self._dir)
        try:
            dir_maker.create()
        except DirectoryAlreadyExists as e:
            # TODO: log this
            pass

    def _make_file(self):
        file_maker = FileMaker(self._path)
        try:
            file_maker.create()
        except FileAlreadyExists as e:
            # TODO: log this
            pass

    def _get_eof_pointer(self) -> int:
        with open(self._path, "r") as f:
            f.seek(0, 2)
            return f.tell()

    def _is_empty(self) -> bool:
        pointer = self._get_eof_pointer()
        return True if pointer == 0 else False

    def _initial_fill(self) -> None:
        pass

    def _setup(self):
        self._make_dir()
        self._make_file()

        if self._is_empty():
            self._initial_fill()

    @staticmethod
    def _validate_time_field(entry: Entry):
        time_ = entry.get("time")
        if not time_:
            raise TimetableEntryMissingTime

        try:
            datetime.strptime(time_, "%H:%M")
        except ValueError:
            raise TimetableEntryWrongTimeFormat

    def add(self, entry: Entry) -> None:
        pass

    def add_batch(self, entries: list[Entry]) -> None:
        pass

    def remove(self, entry: Entry) -> None:
        pass

    def get(self) -> list[Entry]:  # type: ignore
        pass


class TimetableFileJSON(BaseTimetableFile):
    def __init__(self, path: Path | None = None):
        super().__init__(path)

    def _initial_fill(self) -> None:
        with open(self._path, "w") as f:
            json.dump([], f)

    def _rewrite(self, data: list[Entry]):
        with open(self._path, "w") as f:
            json.dump(data, f, indent=2)

    def add(self, to_add: Entry) -> None:
        self._validate_time_field(to_add)

        entries = self.get()
        entries.append(to_add)

        self._rewrite(entries)

    def add_batch(self, to_add: list[Entry]) -> None:
        [self._validate_time_field(item) for item in to_add]

        entries = self.get()
        entries.extend(to_add)

        self._rewrite(entries)

    def remove(self, to_remove: Entry) -> None:
        self._validate_time_field(to_remove)
        entries = self.get()

        try:
            entries.remove(to_remove)
            self._rewrite(entries)
        except ValueError:
            pass

    def get(self) -> list[Entry]:
        with open(self._path, "r") as f:
            return json.load(f)


class TimetableFactory:
    DEFAULT_PATH = ".timetables/timetable.json"
    SUPPORTED_FORMATS = ["json", ]

    def __init__(self, path: Path = DEFAULT_PATH):
        self.path = path
        self.fmt = os.path.splitext(path)[-1]

    def create(self) -> BaseTimetableFile:
        if self.fmt == ".json":
            return TimetableFileJSON(self.path)
        else:
            raise TimetableUnexpectedFormat("Such format is not supported yet")
