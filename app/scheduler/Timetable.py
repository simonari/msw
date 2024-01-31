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

    def add(self, entry: Entry | list[Entry]) -> None:
        pass

    def remove(self, entry: Entry) -> None:
        pass

    def get(self) -> list[Entry]:  # type: ignore
        pass


# class TimetableFileJSON(BaseTimetableFile):
#     def __init__(
#             self,
#             dir_: str | None = None,
#             name: str | None = None
#     ):
#         super().__init__(dir_, name, "json")
#
#     def _rewrite_file(self, data: list[Entry]):
#         with open(self._path, "w") as f:
#             json.dump(data, f, indent=2)
#
#     def _initial_fill(self) -> None:
#         if not self._is_empty():
#             return
#
#         self._rewrite_file([])
#
#     @staticmethod
#     def _is_time_provided(entry: Entry):
#         t = entry.get("time")
#         if t is None:
#             raise TimetableEntryMissingTime("No time was provided")
#
#         try:
#             datetime.strptime(t, "%H:%M")
#         except Exception as e:
#             raise TimetableEntryWrongTimeFormat("Time was provided in wrong format")
#
#     def _add_single(self, entry: Entry) -> None:
#         content = self.get()
#         self._is_time_provided(entry)
#         content.append(entry)
#         content = self._sort(content)
#         self._rewrite_file(content)
#
#     def _add_bulk(self, entries: list[Entry]) -> None:
#         content = self.get()
#         [self._is_time_provided(e) for e in entries]
#         content += entries
#         content = self._sort(content)
#         self._rewrite_file(content)
#
#     @staticmethod
#     def _sort(content: list[Entry]) -> list[Entry]:
#         return sorted(content, key=lambda d: d["time"])
#
#     def add(self, entry: Entry | list[Entry]) -> None:
#         if isinstance(entry, list):
#             self._add_bulk(entry)
#             return
#
#         self._add_single(entry)
#
#     def remove(self, entry: Entry) -> None:
#         pass
#
#     def get(self) -> list[Entry]:
#         with open(self._path, "r") as f:
#             return json.load(f)
#
#
# class Timetable:
#     def __init__(
#             self,
#             dir_: str | None = None,
#             name: str | None = None,
#             fmt: str | None = None
#     ):
#         self.timetable: BaseTimetableFile
#
#         match fmt:
#             case "json":
#                 self.timetable = TimetableFileJSON(dir_, name)
#             case _:
#                 raise TimetableUnexpectedFormat("This format is not supported")
#
#     def get(self) -> list[Entry]:
#         return self.timetable.get()
#
#     def add(self, entry: Entry | list[Entry]) -> None:
#         self.timetable.add(entry)
#
#     def remove(self):
#         pass
