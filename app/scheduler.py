from schedule import Scheduler
from datetime import datetime, time
import asyncio
import json
import os

from .task_manager import download
scheduler = Scheduler()


class DownloadSchedule(Scheduler):
    DEFAULT_CONFIG_PATH = "timetable.json"

    def __init__(self, /, config_path: str = DEFAULT_CONFIG_PATH):
        super().__init__()
        self._loop = asyncio.get_event_loop()
        self._pending: asyncio.Task | None = None
        self._config_path = config_path
        self._setup()

    def _setup(self):
        if not os.path.isfile(os.path.join(os.getcwd(), self._config_path)):
            with open(self._config_path, "w"):
                pass

        with open(self._config_path, "r") as f:
            schedule = []
            try:
                schedule = json.load(f)
            except json.decoder.JSONDecodeError:
                # TODO: log this
                pass

        for task in schedule:
            self.every().day.at(task["time"]) \
                .do(download, task["query"]) \
                .tag("download")

    def _update_config(self, data: list[dict]):
        with open(self._config_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _create_task(query, _time):
        return {"time": _time, "query": query}

    def _add_to_config(self, query, _time):
        with open(self._config_path, "r") as f:
            schedule = []
            try:
                schedule = json.load(f)
            except json.decoder.JSONDecodeError:
                # TODO: log this
                pass

        with open(self._config_path, "w") as f:
            schedule.append(self._create_task(query, _time))
            json.dump(schedule, f, indent=2)

    def _remove_from_config(self, query, _time):
        with open(self._config_path, "rw") as f:
            schedule = []
            try:
                schedule = json.load(f)
            except json.decoder.JSONDecodeError:
                # TODO: log this
                pass

            for task in schedule:
                if task["query"] == query and task["time"] == _time:
                    del task

            json.dump(schedule, f, indent=2)

    async def _start_pending(self):
        while True:
            await asyncio.sleep(1)
            print(f"{datetime.now()} i'm running")
            job = self.get_jobs()[-1]
            print(job.at_time, job.job_func)
            self.run_pending()

    def start(self):
        # self._loop.run_in_executor(None, lambda: asyncio.run(self._start_pending()))
        self._pending = self._loop.create_task(self._start_pending())

    def stop(self):
        if self._pending is None:
            return

        self._pending.cancel()

    @staticmethod
    def with_restart(foo):
        def inner(self, *args, **kwargs):
            self.stop()
            foo(self, *args, *kwargs)
            self.start()

        return inner

    @with_restart
    def add_task(self, query, _time):
        self.every().day.at(_time) \
            .do(download, query) \
            .tag("download")

        self._add_to_config(query, _time)

    @with_restart
    def remove_task(self, query, _time):
        jobs = self.get_jobs()

        for job in jobs:
            if job.at_time == time(_time) and job.job_func.args[0] == query:
                self.cancel_job(job)
            break

        self._remove_from_config(query, _time)
