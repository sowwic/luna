import pymel.core as pm
import unittest

from Luna.test import TestCase
from Luna_rig.core import control
from Luna_rig.core.shape_manager import ShapeManager
from Luna.static import colors


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
        self.assertEqual(instance.name, "arm_ik")
        self.assertEqual(instance.side, "r")
        self.assertEqual(instance.group.ty.get(), 5)
        self.assertTrue(instance.transform.sx.isLocked())
        self.assertTrue(instance.transform.sy.isLocked())
        self.assertTrue(instance.transform.sz.isLocked())

        # Save test file
        pm.renameFile(self.get_temp_filename("control_test_create_default.ma"))
        pm.saveFile(f=1)

    def test_instance_ctor(self):
        ctl1 = control.Control.create(name="arm_ik",
                                      side="r",
                                      attributes="tr",
                                      joint=1,
                                      tag="test")

        inst = control.Control(ctl1.transform)
        self.assertEqual(inst.side, ctl1.side)
        self.assertEqual(inst.name, ctl1.name)
        self.assertEqual(inst.group, ctl1.group)
        self.assertListEqual(inst.offset_list, ctl1.offset_list)
        self.assertEqual(inst.offset, ctl1.offset)
        self.assertEqual(inst.transform, ctl1.transform)
        self.assertEqual(inst.joint, ctl1.joint)
        self.assertEqual(inst.tag, ctl1.tag)

    def test_create_with_parent(self):
        ctl1 = control.Control.create(name="arm_ik",
                                      side="r",
                                      attributes="tr")
        ctl2 = control.Control.create(name="arm_ik",
                                      side="r",
                                      attributes="tr",
                                      parent=ctl1)
        self.assertEqual(ctl2.get_parent(), ctl1.transform)

    def test_set_parent(self):
        ctl1 = control.Control.create(name="arm_ik",
                                      side="r",
                                      attributes="tr")
        ctl2 = control.Control.create(name="arm_ik",
                                      side="r",
                                      attributes="tr")
        ctl2.set_parent(ctl1)
        self.assertEqual(ctl2.get_parent(), ctl1.transform)

    def test_set_color(self):
        instance = control.Control.create(name="arm_ik",
                                          side="r")
        self.assertEqual(ShapeManager.get_color(instance.transform), colors.SideColor[instance.side].value)
        test_color = 17
        instance.color = test_color
        self.assertEqual(ShapeManager.get_color(instance.transform), test_color)


if __name__ == "__main__":
    unittest.main(exit=False)
