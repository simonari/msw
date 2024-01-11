import os
import json


class SchedulerTimetableFormatError(ValueError):
    """Not supported timetable format provided"""


class BaseScheduler:
    def start_pending(self):
        pass

    def stop_pending(self):
        pass

    def add(self):
        pass

    def remove(self):
        pass


class Scheduler(BaseScheduler):
    def __init__(
            self,
            dir_: str | None = None,
    ):
        self.DEFAULT_NAME: str = "timetable"
        self.DEFAULT_FMT: str = "json"
        self.AVAILABLE_FMT: set[str] = {"json", }
        self.DEFAULT_DIR: str = ".timetables"

        self._dir: str
        self._fmt: str
        self._filename: str
        self._path: str

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
            fmt = self.DEFAULT_FMT
        if fmt not in self.AVAILABLE_FMT:
            raise SchedulerTimetableFormatError(f"Such format [{fmt}] is not supported")

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

    def _rewrite_json(self, data: list[dict]):
        with open(self._path, "w") as f:
            json.dump(data, f, indent=2)

    def _initial_fill_json(self):
        self._rewrite_json([])

    def _initial_fill(self):
        match self._fmt:
            case ".json":
                self._initial_fill_json()

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
