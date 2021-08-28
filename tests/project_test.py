import os
import unittest
import luna.workspace
from luna.test import TestCase


class ProjectTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super(ProjectTests, cls).tearDownClass()
        luna.workspace.Project.exit()

    def test_create_project(self):
        creation_path = ProjectTests.get_temp_dirname("testProject")
        test_project = luna.workspace.Project.create(creation_path, silent=True)

        # Assertions
        self.assertTrue(os.path.exists(test_project.path))
        self.assertEqual(luna.workspace.Project.get(), test_project)
        self.assertTrue(os.path.exists(test_project.tag_path))
        self.assertTrue(os.path.exists(test_project.meta_path))

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


if __name__ == "__main__":
    unittest.main(exit=False)
