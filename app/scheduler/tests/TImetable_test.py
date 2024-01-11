import pytest
import os
import json

from ..Timetable import BaseTimetableFile, TimetableFileJSON
from ..Timetable import (
    TimetableEmptyFormat,
    TimetableUnexpectedFormat,
    TimetableEntryMissingTime,
    TimetableEntryWrongTimeFormat,
)


class TestBaseTimetableFile:
    class TestFileCreation:
        def test_no_args(self):
            try:
                tt = BaseTimetableFile()
            except Exception as e:
                assert isinstance(e, TimetableEmptyFormat)

            return 1

        def test_empty_dir(self):
            tt = BaseTimetableFile(name="test", fmt="test")
            assert os.path.exists(tt.DEFAULT_DIR)

            path = os.path.join(tt.DEFAULT_DIR, "test.test")
            assert os.path.exists(path)

            os.remove(path)
            os.rmdir(tt.DEFAULT_DIR)

        def test_empty_name(self):
            tt = BaseTimetableFile(fmt="test")
            assert os.path.exists(tt.DEFAULT_DIR)

            path = os.path.join(tt.DEFAULT_DIR, f"{tt.DEFAULT_NAME}.test")
            assert os.path.exists(path)

            os.remove(path)
            os.rmdir(tt.DEFAULT_DIR)

        def test_empty_fmt(self):
            dir_ = "abcd"
            name = "abcd"
            try:
                tt = BaseTimetableFile(dir_=dir_, name=name)
            except Exception as e:
                assert isinstance(e, TimetableEmptyFormat)

            assert ~os.path.exists(dir_)


class TestTimetableFileJSON:
    class TestFileCreation:
        def test_no_args(self):
            tt = TimetableFileJSON()
            assert os.path.exists(tt.DEFAULT_DIR)

            path = os.path.join(tt.DEFAULT_DIR, f"{tt.DEFAULT_NAME}.{tt._fmt}")
            assert os.path.exists(path)

            os.remove(path)
            os.rmdir(tt.DEFAULT_DIR)

        def test_with_args(self):
            dir_ = "abc"
            name = "def"

            tt = TimetableFileJSON(dir_, name)
            assert os.path.exists(dir_)

            path = os.path.join(dir_, f"{name}.{tt._fmt}")
            assert os.path.exists(path)

            os.remove(path)
            os.rmdir(dir_)

        def test_initial_fill(self):
            tt = TimetableFileJSON()

            with open(tt._path, "r") as f:
                content = json.load(f)

            assert content == []

            os.remove(tt._path)
            os.rmdir(tt._dir)

    class TestGetInterface:
        def test_get_on_creation(self):
            tt = TimetableFileJSON()

            result = tt.get()

            assert result == []

            os.remove(tt._path)
            os.rmdir(tt._dir)

    class TestAddInterface:
        def test_add_single(self):
            tt = TimetableFileJSON()

            try:
                tt.add({"test": "test"})
            except Exception as e:
                assert isinstance(e, TimetableEntryMissingTime)

            try:
                tt.add({"test": "test", "time": "15:15:00"})
            except Exception as e:
                assert isinstance(e, TimetableEntryWrongTimeFormat)

            try:
                tt.add({"test": "test", "time": "15"})
            except Exception as e:
                assert isinstance(e, TimetableEntryWrongTimeFormat)

            tt.add({"test": "test", "time": "16:00"})

            result = tt.get()
            assert result == [{"test": "test", "time": "16:00"}]

            tt.add({"test": "test", "time": "15:00"})

            result = tt.get()
            assert result == [
                {"test": "test", "time": "15:00"},
                {"test": "test", "time": "16:00"}
            ]

            os.remove(tt._path)
            os.rmdir(tt._dir)

        def test_add_bulk(self):
            tt = TimetableFileJSON()

            try:
                tt.add([
                    {"test1": "test1"},
                    {"test2": "test2"},
                ])
            except Exception as e:
                assert isinstance(e, TimetableEntryMissingTime)

            try:
                tt.add([
                    {"test1": "test1", "time": "15:00"},
                    {"test2": "test2"},
                ])
            except Exception as e:
                assert isinstance(e, TimetableEntryMissingTime)

            try:
                tt.add([
                    {"test1": "test1", "time": "16:00"},
                    {"test2": "test2", "time": "16"},
                ])
            except Exception as e:
                assert isinstance(e, TimetableEntryWrongTimeFormat)

            try:
                tt.add([
                    {"test1": "test1", "time": "16:00"},
                    {"test2": "test2", "time": "16:00:01"},
                ])
            except Exception as e:
                assert isinstance(e, TimetableEntryWrongTimeFormat)

            tt.add([
                {"test1": "test1", "time": "17:00"},
                {"test2": "test2", "time": "16:00"},
            ])

            result = tt.get()
            assert result == [
                {"test2": "test2", "time": "16:00"},
                {"test1": "test1", "time": "17:00"},
            ]

            tt.add([
                {"test3": "test3", "time": "19:00"},
                {"test4": "test4", "time": "13:00"},
            ])

            result = tt.get()
            assert result == [
                {"test4": "test4", "time": "13:00"},
                {"test2": "test2", "time": "16:00"},
                {"test1": "test1", "time": "17:00"},
                {"test3": "test3", "time": "19:00"},
            ]

            os.remove(tt._path)
            os.rmdir(tt._dir)
