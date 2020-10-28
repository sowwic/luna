import unittest
import pymel.core as pm


class TestCase(unittest.TestCase):
    """
    Base class for unit test cases run in Maya.

    Tests do not have to inherit from this TestCase but this derived TestCase contains convenience
    functions to load/unload plug-ins and clean up temporary files.
    """

    files_created = []
    plugins_loaded = set()

    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()

    @classmethod
    def delete_temp_files(cls):
        pass

    @classmethod
    def unload_plugins(cls):
        pass

    @classmethod
    def get_temp_filename(cls, filename):
        pass
