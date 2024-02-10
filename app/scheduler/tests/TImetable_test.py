import pytest
import os
import json

from ..Timetable import BaseTimetableFile, TimetableFileJSON, TimetableFactory
from ..Timetable import (
    TimetableEmptyFormat,
    TimetableUnexpectedFormat,
    TimetableEntryMissingTime,
    TimetableEntryWrongTimeFormat,
)


@pytest.fixture
def instantiate_base_timetable():
    tt = BaseTimetableFile()
    path = tt._path
    dir_ = tt._dir
    filename = tt._filename
    ext = tt._ext

    print(f"Instance: {tt}\n"
          f"Path: {path}\n"
          f"Directory: {dir_}\n"
          f"Filename: {filename}\n"
          f"Extension: {ext}\n")

    yield tt, path, dir_, filename, ext

    print("\nClearing files...\n")
    os.remove(path)
    os.removedirs(dir_)


@pytest.fixture
def instantiate_json_timetable():
    timetable = TimetableFileJSON()

    path = timetable._path
    dir_ = timetable._dir

    yield timetable, path, dir

    os.remove(path)
    os.removedirs(dir_)


class TestBaseTimetableFile:
    class TestFileCreation:
        def test_no_args(self, instantiate_base_timetable):
            tt, path, dir_, filename, ext = instantiate_base_timetable

            assert os.path.isdir(dir_)
            assert os.path.isfile(path)

        def test_local_file(self):
            tt = BaseTimetableFile("timetable")
            path = tt._path
            dir_ = tt._dir
            filename = tt._filename
            ext = tt._ext

            print(f"Instance: {tt}\n"
                  f"Path: {path}\n"
                  f"Directory: {dir_}\n"
                  f"Filename: {filename}\n"
                  f"Extension: {ext}\n")

            assert os.path.isfile(path)

            os.remove(path)

        def test_nested_dirs(self):
            tt = BaseTimetableFile("nested/dir/file")
            path = tt._path
            dir_ = tt._dir
            filename = tt._filename
            ext = tt._ext

            print(f"Instance: {tt}\n"
                  f"Path: {path}\n"
                  f"Directory: {dir_}\n"
                  f"Filename: {filename}\n"
                  f"Extension: {ext}\n")

            assert os.path.isfile(path)

            os.remove(path)
            os.removedirs(dir_)


class TestTimetableFileJSON:
    class TestFileCreation:
        def test_no_args(self):
            timetable = TimetableFileJSON()

            dir_ = timetable._dir
            path = timetable._path

            assert os.path.isdir(dir_)
            assert os.path.isfile(path)

            os.remove(path)
            os.removedirs(dir_)

        def test_local_file(self):
            timetable = TimetableFileJSON("timetable.json")

            path = timetable._path

            assert os.path.isfile(path)

            os.remove(path)

        def test_nested_dirs(self):
            tt = TimetableFileJSON("nested/dir/file")

            path = tt._path
            dir_ = tt._dir

            assert os.path.isfile(path)

            os.remove(path)
            os.removedirs(dir_)

    class TestContentOperations:
        def test_initial_fill(self, instantiate_json_timetable):
            timetable, path, dir_ = instantiate_json_timetable

            assert timetable.get() == []

        def test_single_add(self, instantiate_json_timetable):
            timetable, path, dir_ = instantiate_json_timetable

            to_add = {"time": "00:00"}
            accumulated = [to_add]
            timetable.add(to_add)

            assert timetable.get() == accumulated

            to_add = {"time": "01:00"}
            accumulated.append(to_add)
            timetable.add(to_add)

            assert timetable.get() == accumulated

            try:
                timetable.add({"without_time_field": ""})
            except Exception as e:
                assert isinstance(e, TimetableEntryMissingTime)

            try:
                timetable.add({"time": "wrong_time_format"})
            except Exception as e:
                assert isinstance(e, TimetableEntryWrongTimeFormat)

        def test_batch_add(self, instantiate_json_timetable):
            timetable, path, dir_ = instantiate_json_timetable

            to_add = [{"time": "00:00"}, {"time": "01:00"}]
            accumulated = to_add
            timetable.add_batch(to_add)

            assert timetable.get() == accumulated

            to_add = [{"time": "02:00"}, {"time": "03:00"}]
            accumulated.extend(to_add)
            timetable.add_batch(to_add)

            assert timetable.get() == accumulated

            try:
                timetable.add_batch([{"without_time_field": ""}, {"time": "12:00"}])
            except Exception as e:
                assert isinstance(e, TimetableEntryMissingTime)

            try:
                timetable.add_batch([{"time": "wrong_time_format"}, {"time": "12:00"}])
            except Exception as e:
                assert isinstance(e, TimetableEntryWrongTimeFormat)

        def test_remove(self, instantiate_json_timetable):
            timetable, path, dir_ = instantiate_json_timetable

            to_add = [{"time": "00:00"}, {"time": "01:00"}]
            to_remove = {"time": "00:00"}

            timetable.add_batch(to_add)

            timetable.remove(to_remove)

            assert timetable.get() == [to_add[1]]

            to_remove = {"time": "02:00"}
            timetable.remove(to_remove)

            assert timetable.get() == [to_add[1]]

            try:
                timetable.remove({"without_time_field": ""})
            except Exception as e:
                assert isinstance(e, TimetableEntryMissingTime)

            try:
                timetable.remove({"time": "wrong_time_format"})
            except Exception as e:
                assert isinstance(e, TimetableEntryWrongTimeFormat)


class TestTimetableFactory:
    def test_empty(self):
        factory = TimetableFactory()
        timetable = factory.create()

        assert isinstance(timetable, TimetableFileJSON)

        os.remove(timetable._path)
        os.removedirs(timetable._dir)

    def test_json(self):
        path = "path/to/timetable.json"
        factory = TimetableFactory(path)

        timetable = factory.create()

        assert isinstance(timetable, TimetableFileJSON)

        os.remove(timetable._path)
        os.removedirs(timetable._dir)

    def test_not_supported(self):
        path = "bad.format"
        factory = TimetableFactory(path)

        try:
            timetable = factory.create()
        except Exception as e:
            assert isinstance(e, TimetableUnexpectedFormat)