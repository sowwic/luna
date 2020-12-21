import pymel.core as pm
import unittest

from Luna.test import TestCase
from Luna_rig.core import control
from Luna_rig.core.shape_manager import ShapeManager
from Luna_rig.functions import nameFn
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
        self.assertTrue(instance.is_control(instance.transform))
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
        self.assertTrue(control.Control.is_control(inst.transform))
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

    def test_insert_offset(self):
        instance = control.Control.create(name="arm_ik",
                                          side="r",
                                          offset_grp=True)
        self.assertEqual(instance.offset_list[0], instance.offset)
        old_offset = instance.offset
        expected_name = nameFn.generate_name(name=[instance.name, "extra"], side="r", suffix="ofs")
        new_offset = instance.insert_offset(extra_name="extra")
        self.assertEqual(new_offset.name(), expected_name)
        self.assertEqual(instance.offset, new_offset)
        self.assertListEqual([old_offset, new_offset], instance.offset_list)

    def test_rename(self):
        instance = control.Control.create(name="arm_ik",
                                          side="r",
                                          offset_grp=True,
                                          joint=1)
        instance.insert_offset(extra_name="extra")

        # Expectations
        expected_ctl_name = nameFn.generate_name(name="leg", side="l", suffix="ctl")
        expected_grp_name = nameFn.generate_name(name="leg", side="l", suffix="grp")
        expected_jnt_name = nameFn.generate_name(name="leg", side="l", suffix="cjnt")
        expected_ofs_name = nameFn.generate_name(name="leg", side="l", suffix="ofs")
        expected_extra_ofs_name = nameFn.generate_name(name="leg_extra", side="l", suffix="ofs")

        instance.rename(side="l", name="leg")
        self.assertEqual(instance.transform.name(), expected_ctl_name)
        self.assertEqual(instance.group.name(), expected_grp_name)
        self.assertEqual(instance.joint.name(), expected_jnt_name)
        self.assertEqual(instance.offset_list[0].name(), expected_ofs_name)
        self.assertEqual(instance.offset.name(), expected_extra_ofs_name)


if __name__ == "__main__":
    unittest.main(exit=False)
