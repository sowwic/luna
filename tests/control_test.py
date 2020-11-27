import pymel.core as pm
import unittest

from Luna import Logger
from Luna.test import TestCase
from Luna_rig.core import control
reload(control)


class ControlTests(TestCase):
    def setUp(self):
        pm.newFile(f=1)

    def tearDown(self):
        pm.newFile(f=1)

    def test_create_default(self):
        guide = pm.spaceLocator(n="temp_guide")
        guide.ty.set(5)
        instance = control.Control.create(name="arm_ik",
                                          side="r",
                                          object_to_match=guide,
                                          attributes="tr",
                                          delete_match_object=False)

        # Assertions
        self.assertEqual(instance.data.name, "arm_ik")
        self.assertEqual(instance.data.side, "r")
        self.assertEqual(instance.group.ty.get(), 5)
        self.assertTrue(instance.transform.sx.isLocked())
        self.assertTrue(instance.transform.sy.isLocked())
        self.assertTrue(instance.transform.sz.isLocked())

        # Save test file
        pm.renameFile(self.get_temp_filename("control_test_create_default.ma"))
        pm.saveFile(f=1)


if __name__ == "__main__":
    unittest.main(exit=False)
