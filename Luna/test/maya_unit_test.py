import os
import shutil
import unittest
import pymel.core as pm
from Luna import Config
from Luna import Logger


class TestVars:
    delete_files = "tests.delete_files"
    delete_dirs = "tests.delete_dirs"
    temp_dir = "tests.temp_dir"


class TestCase(unittest.TestCase):
    """
    Base class for unit test cases run in Maya.

    Tests do not have to inherit from this TestCase but this derived TestCase contains convenience
    functions to load/unload plug-ins and clean up temporary files.
    """
    files_created = []
    dirs_created = []
    plugins_loaded = set()

    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
        cls.delete_temp_files()
        cls.unload_plugins()

    @classmethod
    def load_plugin(cls, plugin):
        pm.loadPlugin(plugin, qt=1)
        cls.plugins_loaded.add(plugin)

    @classmethod
    def unload_plugins(cls):
        for plugin in cls.plugins_loaded:
            pm.unloadPlugin(plugin)
        cls.plugins_loaded = set()

    @classmethod
    def delete_temp_files(cls):
        """Delete the temp files in the cache and clear the cache."""
        # If we don't want to keep temp files around for debugging purposes, delete them when
        # all tests in this TestCase have been run
        if Config.get(TestVars.delete_dirs, True):
            for d in cls.dirs_created:
                if os.path.isdir(d):
                    shutil.rmtree(d)
                    Logger.info("Deleted dir: {0}".format(d))
            cls.dirs_created = []

        if Config.get(TestVars.delete_files, True):
            for f in cls.files_created:
                if os.path.exists(f):
                    os.remove(f)
                    Logger.info("Deleted temp file: {0}".format(f))
            cls.files_created = []

    @classmethod
    def get_temp_filename(cls, file_name):
        temp_dir = Config.get(TestVars.temp_dir)
        if not temp_dir:
            temp_dir = pm.internalVar(utd=1)

        base_name, ext = os.path.splitext(file_name)
        path = os.path.join(temp_dir, base_name + ext)
        count = 0
        while os.path.exists(path):
            count += 1
            path = os.path.join(temp_dir, "{0}{1}{2}".format(base_name, count, ext))
        cls.files_created.append(path)

        return path

    @classmethod
    def get_temp_dirname(cls, dir_name):
        temp_dir = Config.get(TestVars.temp_dir)
        if not temp_dir:
            temp_dir = pm.internalVar(utd=1)

        path = os.path.join(temp_dir, dir_name)
        count = 0
        while os.path.exists(path):
            count += 1
            path = os.path.join(temp_dir, "{0}{1}".format(dir_name, count))
        cls.dirs_created.append(path)

        return path
