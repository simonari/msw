import pytest
import os

from ..DirMaker import (
    DirMaker,
    DirectoryAlreadyExists
)


class TestDirMaker:
    class TestInitialization:
        def test_without_args(self):
            dirmaker = DirMaker()

            assert dirmaker.directory == dirmaker.DEFAULT_DIRECTORY_NAME

        def test_with_args(self):
            dir_to_make = "Some Directory"

            dirmaker = DirMaker(dir_to_make)

            assert dirmaker.directory == dir_to_make

    class TestCreation:
        def test_locally(self):
            dir_to_make = "Local directory"
            dirmaker = DirMaker(dir_to_make)

            dirmaker.create()

            os.path.exists(dir_to_make)
            os.rmdir(dir_to_make)

        def test_nested(self):
            dir_to_make = "First/Second/Third"
            dirmaker = DirMaker(dir_to_make)

            dirmaker.create()

            os.path.exists(dir_to_make)
            os.removedirs(dir_to_make)

        def test_exists(self):
            dir_to_make = "Exists"
            dirmaker = DirMaker(dir_to_make)
            dirmaker.create()

            try:
                dirmaker.create()
            except Exception as e:
                assert isinstance(e, DirectoryAlreadyExists)

            os.removedirs(dir_to_make)