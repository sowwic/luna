import os
import unittest
import luna
from luna.test import TestCase


class ProjectTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super(ProjectTests, cls).tearDownClass()
        luna.workspace.Project.exit()
        luna.workspace.Project.refresh_recent()

    def test_create_project(self):
        creation_path = ProjectTests.get_temp_dirname("testProject")
        test_project = luna.workspace.Project.create(creation_path)

        # Assertions
        self.assertTrue(os.path.exists(test_project.path))
        self.assertEqual(luna.workspace.Project.get(), test_project)
        self.assertTrue(os.path.exists(test_project.tag_path))
        self.assertTrue(os.path.exists(test_project.meta_path))
        self.assertEqual(luna.Config.get(luna.ProjectVars.previous_project), test_project.path)
        self.assertIn([test_project.name, test_project.path], luna.Config.get(luna.ProjectVars.recent_projects))

    def test_isProject(self):
        creation_path = ProjectTests.get_temp_dirname("testProject")
        test_project = luna.workspace.Project.create(creation_path)
        self.assertTrue(luna.workspace.Project.is_project(test_project.path))
        self.assertFalse(luna.workspace.Project.is_project(test_project.path + "/newFolder"))

    def test_set_project(self):
        creation_path = ProjectTests.get_temp_dirname("testProject")
        luna.workspace.Project.create(creation_path)
        luna.workspace.Project.exit()
        test_project = luna.workspace.Project.set(creation_path)

        # Assertions
        self.assertTrue(os.path.exists(test_project.path))
        self.assertEqual(luna.workspace.Project.get(), test_project)
        self.assertTrue(os.path.exists(test_project.tag_path))
        self.assertTrue(os.path.exists(test_project.meta_path))
        self.assertEqual(luna.Config.get(luna.ProjectVars.previous_project), test_project.path)
        self.assertIn([test_project.name, test_project.path], luna.Config.get(luna.ProjectVars.recent_projects))


if __name__ == "__main__":
    unittest.main(exit=False)
