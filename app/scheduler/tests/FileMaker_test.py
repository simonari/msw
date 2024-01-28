import pytest
import os

from ..FileMaker import FileMaker


class TestFileMaker:
    class TestInitialization:
        def test_without_args(self):
            file_maker = FileMaker()

            assert file_maker.path == file_maker.DEFAULT_PATH

        def test_with_args(self):
            filename_to_make = "test"

            file_maker = FileMaker(filename_to_make)

            assert file_maker.path == filename_to_make

    class TestCreation:
        def test_locally(self):
            filename_to_make = "Local"
            file_maker = FileMaker(filename_to_make)

            file_maker.create()

            assert os.path.exists(filename_to_make)
            os.remove(filename_to_make)

        def test_relative_directory(self):
            directory = "test"
            os.makedirs(directory)

            path_of_file_to_make = os.path.join(directory, "relative")
            file_maker = FileMaker(path_of_file_to_make)

            file_maker.create()

            assert os.path.exists(path_of_file_to_make)
            os.remove(path_of_file_to_make)
            os.removedirs(directory)

        def test_nested_directory(self):
            directory = "nested/directory"
            os.makedirs(directory)

            path_of_file_to_make = os.path.join(directory, "relative")
            file_maker = FileMaker(path_of_file_to_make)

            file_maker.create()

            assert os.path.exists(path_of_file_to_make)
            os.remove(path_of_file_to_make)
            os.removedirs(directory)
