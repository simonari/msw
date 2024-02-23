import asyncio
import os

from .Timetable import BaseTimetableFile, TimetableFactory
from schedule import Scheduler

from typing import Callable

TaskEntry = dict[str, str]
Path = os.PathLike | str


class BaseScheduler:
    DEFAULT_TIMETABLE_PATH = ".timetables/timetable.json"

    def __init__(self, func: Callable[..., None], path: Path = DEFAULT_TIMETABLE_PATH):
        self._scheduler = Scheduler()
        self.timetable: BaseTimetableFile = self._create_timetable(path)
        self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._task: asyncio.Task | None = None
        self.func: Callable[..., None] = func

        self._load()

    @staticmethod
    def _create_timetable(path: Path) -> BaseTimetableFile:
        factory = TimetableFactory(path)
        return factory.create()

    def start(self):
        self._task = self._loop.create_task(self._run_pending())

    def stop(self):
        self._task.cancel()

    async def _run_pending(self):
        while True:
            await asyncio.sleep(1)
            job = self._scheduler.get_jobs()[-1]
            print("i'm running")
            self._scheduler.run_pending()

    @staticmethod
    def _parse_task(task: TaskEntry) -> tuple[str, dict[str, str]]:
        task_time = task["time"]
        del task["time"]
        # returns time and other params
        return task_time, task

    def _load(self):
        tasks = self.timetable.get()
        for task in tasks:
            time_, params = self._parse_task(task)
            self._scheduler.every().day.at(time_).do(self.func, **params)

    @staticmethod
    def with_restart(foo):
        def inner(self, *args, **kwargs):
            self.stop()
            foo(self, *args, **kwargs)
            self.start()

    def _add_task_to_scheduler(self, task: TaskEntry) -> None:
        task_copy = task.copy()
        time_, params = self._parse_task(task_copy)
        self._scheduler.every().day.at(time_).do(self.func, **params)

    @with_restart
    def add_batch(self, tasks: list[TaskEntry]) -> None:
        self.timetable.add_batch(tasks)

        for task in tasks:
            self._add_task_to_scheduler(task)

    @with_restart
    def add(self, task: TaskEntry):
        self.timetable.add(task)
        self._add_task_to_scheduler(task)

    @with_restart
    def remove(self):
        pass

    def get(self) -> list[TaskEntry]:
        return self.timetable.get()
