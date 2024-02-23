import asyncio

import pytest
import os

from ..Scheduler import BaseScheduler
from ..Timetable import (
    TimetableUnexpectedFormat
)


@pytest.fixture
def foo_example():
    def f():
        print("a")

    return f


@pytest.fixture
def instantiate_scheduler_json(foo_example):
    scheduler = BaseScheduler(foo_example)
    dir_ = scheduler.timetable._dir
    path = scheduler.timetable._path

    print(f"Instance: {scheduler}\nDirectory: {dir_}\nPath: {path}")
    yield scheduler, dir_, path
    print(f"Clearing files...")

    os.remove(path)
    os.rmdir(dir_)


@pytest.fixture
def task_list_a() -> list[dict[str, str]]:
    return [
        {"task": "test_1", "time": "00:10"},
        {"task": "test_2", "time": "00:20"},
        {"task": "test_3", "time": "00:30"},
        {"task": "test_4", "time": "00:40"},
    ]


class TestScheduler:
    class TestInitialization:
        def test_init_empty_fmt(self, foo_example):
            try:
                s = BaseScheduler(foo_example)
            except Exception as e:
                assert isinstance(e, TimetableUnexpectedFormat)

        def test_init_json(self, instantiate_scheduler_json):
            s, d, p = instantiate_scheduler_json
            assert os.path.exists(p)

    class TestAddingTasks:
        @pytest.mark.asyncio
        async def test_add_single(self, instantiate_scheduler_json, task_list_a):
            scheduler, d, p = instantiate_scheduler_json

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            scheduler.start()
            await asyncio.sleep(2)
            scheduler.stop()

            # scheduler.add({"time": "00:00", "some": "params"})

            # tasks = task_list_a
            #
            # for i, t in enumerate(tasks):
            #     s.add(t)
            #     assert s.get() == tasks[:i + 1]
