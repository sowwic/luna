import os
import shutil
import unittest
import logging
import pymel.core as pm
from Luna import Config
from Luna import Logger
from Luna import TestVars
from Luna.static import directories


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

        if Config.get(TestVars.delete_files, default=True):
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
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

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


class TestResult(unittest.TextTestResult):
    """Customize the test result so we can do things like do a file new between each test and suppress script
    editor output.
    """

    def startTestRun(self):
        """Called before any tests are run."""
        super(TestResult, self).startTestRun()
        ScriptEditorState.suppress_output()
        if Config.get(TestVars.buffer_output, default=True):
            # Disable any logging while running tests. By disabling critical, we are disabling logging
            # at all levels below critical as well
            logging.disable(logging.CRITICAL)

    def stopTestRun(self):
        """Called after all tests are run."""
        if Config.get(TestVars.buffer_output, default=True):
            # Restore logging state
            logging.disable(logging.NOTSET)
        ScriptEditorState.restore_output()
        super(TestResult, self).stopTestRun()

    def stopTest(self, test):
        """Called after an individual test is run.

        Args:
            test ([type]): [description]
        """
        super(TestResult, self).stopTest(test)
        if Config.get(TestVars.new_file, default=True):
            pm.newFile(f=1)


class ScriptEditorState(object):
    """Provides methods to suppress and restore script editor output."""
    # Used to restore logging states in the script editor
    suppress_results = None
    suppress_errors = None
    suppress_warnings = None
    suppress_info = None

    @classmethod
    def suppress_output(cls):
        """Hides all script editor output."""
        if Config.get(TestVars.buffer_output, default=True):
            cls.suppress_results = pm.scriptEditorInfo(q=True, suppressResults=True)
            cls.suppress_errors = pm.scriptEditorInfo(q=True, suppressErrors=True)
            cls.suppress_warnings = pm.scriptEditorInfo(q=True, suppressWarnings=True)
            cls.suppress_info = pm.scriptEditorInfo(q=True, suppressInfo=True)
            pm.scriptEditorInfo(
                e=True,
                suppressResults=True,
                suppressInfo=True,
                suppressWarnings=True,
                suppressErrors=True,
            )

    @classmethod
    def restore_output(cls):
        """Restores the script editor output settings to their original values."""
        if None not in {
            cls.suppress_results,
            cls.suppress_errors,
            cls.suppress_warnings,
            cls.suppress_info,
        }:
            pm.scriptEditorInfo(
                e=True,
                suppressResults=cls.suppress_results,
                suppressInfo=cls.suppress_info,
                suppressWarnings=cls.suppress_warnings,
                suppressErrors=cls.suppress_errors,
            )


def run_all_tests():
    test_suite = unittest.TestLoader().discover(start_dir=directories.TEST_DIR_PATH, pattern="*_test.py")
    Logger.info("Running {0} tests...".format(test_suite.countTestCases()))
    test_runner = unittest.TextTestRunner(verbosity=2, resultclass=TestResult)
    test_runner.failfast = False
    test_runner.buffer = Config.get(TestVars.buffer_output, default=True)
    test_runner.run(test_suite)


if __name__ == "__main__":
    run_all_tests()
