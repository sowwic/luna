import unittest
import pymel.core as pm
from Luna.test import TestCase
from Luna_rig.functions import jointFn
reload(jointFn)


class JointFnTests(TestCase):

    def setUp(self):
        pm.newFile(f=1)

    def tearDown(self):
        pm.newFile(f=1)

    def test_joint_chain(self):
        # Setup test scene
        pm.joint(n="c_spine_ik_00_jnt", p=[-1.447, 0, -0.979])
        pm.joint(n="c_spine_ik_01_jnt", p=[6.67, 0, 0], r=1)
        pm.joint(n="c_spine_ik_02_jnt", p=[5.06, 0, 0], r=1)
        pm.joint(n="c_spine_ik_03_jnt", p=[5.06, 0, 0], r=1)

        # Assertions
        expected_chain = ["c_spine_ik_00_jnt", "c_spine_ik_01_jnt", "c_spine_ik_02_jnt", "c_spine_ik_03_jnt"]
        result_chain = jointFn.joint_chain("c_spine_ik_00_jnt")
        self.assertListEqual(result_chain, expected_chain)

        # Save test scene
        pm.renameFile(self.get_temp_filename("jointFn_test_joint_chain.ma"))
        pm.saveFile(f=1)

    def test_duplicate_chain_replace_side(self):
        # Setup test scene
        pm.joint(n="c_spine_ik_00_jnt", p=[-1.447, 0, -0.979])
        pm.joint(n="c_spine_ik_01_jnt", p=[6.67, 0, 0], r=1)
        pm.joint(n="c_spine_ik_02_jnt", p=[5.06, 0, 0], r=1)
        pm.joint(n="c_spine_ik_03_jnt", p=[5.06, 0, 0], r=1)
        jointFn.duplicate_chain(start_joint="c_spine_ik_00_jnt", replace_side="l")

        # Assertions
        self.assertTrue(pm.objExists("l_spine_ik_00_jnt"))
        self.assertTrue(pm.objExists("l_spine_ik_01_jnt"))
        self.assertTrue(pm.objExists("l_spine_ik_02_jnt"))
        self.assertTrue(pm.objExists("l_spine_ik_03_jnt"))

        # Save test scene
        pm.renameFile(self.get_temp_filename("jointFn_test_duplicate_chain_replace_side.ma"))
        pm.saveFile(f=1)

    def test_duplicate_chain_start_end(self):
        # Setup test scene
        pm.joint(n="c_spine_ik_00_jnt", p=[-1.447, 0, -0.979])
        pm.joint(n="c_spine_ik_01_jnt", p=[6.67, 0, 0], r=1)
        pm.joint(n="c_spine_ik_02_jnt", p=[5.06, 0, 0], r=1)
        pm.joint(n="c_spine_ik_03_jnt", p=[5.06, 0, 0], r=1)
        duplicated_chain = jointFn.duplicate_chain(start_joint="c_spine_ik_01_jnt", end_joint="c_spine_ik_02_jnt", replace_name=["arm", "fk"])

        # Assertions
        self.assertTrue(pm.objExists("c_arm_fk_00_jnt"))
        self.assertTrue(pm.objExists("c_arm_fk_01_jnt"))
        self.assertEqual(duplicated_chain[0].getTranslation(), pm.PyNode("c_spine_ik_01_jnt").getTranslation())

        # Save test scene
        pm.renameFile(self.get_temp_filename("jointFn_test_duplicate_chain_start_end.ma"))
        pm.saveFile(f=1)


if __name__ == "__main__":
    unittest.main(exit=False)
