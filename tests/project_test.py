import os
import unittest
from Luna.workspace.project import Project
from Luna.workspace.project import ProjectVars
from Luna.core.config import Config
from Luna.utils import environFn
from Luna.test import TestCase

# prev_path = Config.get(project.ProjectVars.previous_project, "")
# path = QtWidgets.QFileDialog.getExistingDirectory(None, "Create Luna project", prev_path)
# if path:
#     test_project = project.Project.create(path)


class ProjectTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super(ProjectTests, cls).tearDownClass()
        Project.exit()
        Project.refresh_recent()

    def test_create_project(self):
        creation_path = ProjectTests.get_temp_dirname("testProject")
        test_project = Project.create(creation_path)

        # Assertions
        self.assertTrue(os.path.exists(test_project.path))
        self.assertEqual(environFn.get_project_var(), test_project)
        self.assertTrue(os.path.exists(test_project.tag_path))
        self.assertTrue(os.path.exists(test_project.meta_path))
        self.assertEqual(Config.get(ProjectVars.previous_project), test_project.path)
        self.assertIn([test_project.name, test_project.path], Config.get(ProjectVars.recent_projects))

    def test_isProject(self):
        creation_path = ProjectTests.get_temp_dirname("testProject")
        test_project = Project.create(creation_path)
        self.assertTrue(Project.is_project(test_project.path))
        self.assertFalse(Project.is_project(test_project.path + "/newFolder"))

    def test_set_project(self):
        creation_path = ProjectTests.get_temp_dirname("testProject")
        Project.create(creation_path)
        Project.exit()
        test_project = Project.set(creation_path)

        # Assertions
        self.assertTrue(os.path.exists(test_project.path))
        self.assertEqual(environFn.get_project_var(), test_project)
        self.assertTrue(os.path.exists(test_project.tag_path))
        self.assertTrue(os.path.exists(test_project.meta_path))
        self.assertEqual(Config.get(ProjectVars.previous_project), test_project.path)
        self.assertIn([test_project.name, test_project.path], Config.get(ProjectVars.recent_projects))


if __name__ == "__main__":
    unittest.main(exit=False)
