import os
import json
from datetime import datetime

Entry = dict[str, str]


class TimetableEmptyFormat(ValueError):
    """No timetable format provided"""


class TimetableUnexpectedFormat(ValueError):
    """Not supported timetable format provided"""


class TimetableEntryMissingTime(ValueError):
    """No time provided in entry"""


class TimetableEntryWrongTimeFormat(ValueError):
    """Wrong time format"""


class BaseTimetableFile:
    def __init__(
            self,
            dir_: str | None = None,
            name: str | None = None,
            fmt: str | None = None
    ):
        self.DEFAULT_DIR: str = ".timetables"
        self.DEFAULT_NAME: str = "timetable"

        self._setup(dir_, name, fmt)

    def _setup_dir(
            self,
            dir_: str | None = None
    ):
        if dir_ is None:
            dir_ = self.DEFAULT_DIR

        if not os.path.isdir(dir_):
            os.makedirs(dir_, exist_ok=True)

        self._dir = dir_

    def _setup_file(
            self,
            name: str | None = None,
            fmt: str | None = None
    ) -> bool:
        if name is None:
            name = self.DEFAULT_NAME
        if fmt is None:
            os.rmdir(self._dir)
            raise TimetableEmptyFormat("Not supported timetable format provided")

        filename: str = ".".join([name, fmt])
        path: str = os.path.join(self._dir, filename)

        was_created: bool = False
        if not os.path.exists(path):
            was_created = True
            open(path, "w").close()

        self._filename = filename
        self._fmt = fmt
        self._path = path

        return was_created

    def _is_empty(self) -> bool:
        with open(self._path, "r") as f:
            f.seek(0, 2)
            pointer = f.tell()

        if pointer == 0:
            return True

        return False

    def _initial_fill(self) -> None:
        pass

    def _setup(
            self,
            dir_: str | None = None,
            name: str | None = None,
            fmt: str | None = None
    ):
        self._setup_dir(dir_)
        was_created = self._setup_file(name, fmt)

        if was_created:
            self._initial_fill()

    def add(self, entry: Entry | list[Entry]) -> None:
        pass

    def remove(self, entry: Entry) -> None:
        pass

    def get(self) -> list[Entry]:  # type: ignore
        pass


class TimetableFileJSON(BaseTimetableFile):
    def __init__(
            self,
            dir_: str | None = None,
            name: str | None = None
    ):
        super().__init__(dir_, name, "json")

    def _rewrite_file(self, data: list[Entry]):
        with open(self._path, "w") as f:
            json.dump(data, f, indent=2)

    def _initial_fill(self) -> None:
        if not self._is_empty():
            return

        self._rewrite_file([])

    @staticmethod
    def _is_time_provided(entry: Entry):
        t = entry.get("time")
        if t is None:
            raise TimetableEntryMissingTime("No time was provided")

        try:
            datetime.strptime(t, "%H:%M")
        except Exception as e:
            raise TimetableEntryWrongTimeFormat("Time was provided in wrong format")

    def _add_single(self, entry: Entry) -> None:
        content = self.get()
        self._is_time_provided(entry)
        content.append(entry)
        content = self._sort(content)
        self._rewrite_file(content)

    def _add_bulk(self, entries: list[Entry]) -> None:
        content = self.get()
        [self._is_time_provided(e) for e in entries]
        content += entries
        content = self._sort(content)
        self._rewrite_file(content)

    @staticmethod
    def _sort(content: list[Entry]) -> list[Entry]:
        return sorted(content, key=lambda d: d["time"])

    def add(self, entry: Entry | list[Entry]) -> None:
        if isinstance(entry, list):
            self._add_bulk(entry)
            return

        self._add_single(entry)

    def remove(self, entry: Entry) -> None:
        pass

    def get(self) -> list[Entry]:
        with open(self._path, "r") as f:
            return json.load(f)


class Timetable:
    def __init__(
            self,
            dir_: str | None = None,
            name: str | None = None,
            fmt: str | None = None
    ):
        self.timetable: BaseTimetableFile

        match fmt:
            case "json":
                self.timetable = TimetableFileJSON(dir_, name)
            case _:
                raise TimetableUnexpectedFormat("This format is not supported")

    def get(self) -> list[Entry]:
        return self.timetable.get()

    def add(self, entry: Entry | list[Entry]) -> None:
        self.timetable.add(entry)

    def remove(self):
        pass
