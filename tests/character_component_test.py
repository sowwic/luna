import pymel.core as pm
import unittest

from luna import static
from luna.test import TestCase
import luna_rig


class CharacterTests(TestCase):
    def setUp(self):
        pm.newFile(f=1)

    def tearDown(self):
        super(CharacterTests, self).tearDown()
        pm.newFile(f=1)

    def test_create_default(self):
        instance = luna_rig.components.Character.create()

        # Assertions
        # Metanode attributes
        self.assertTrue(pm.hasAttr(instance.pynode, "rootCtl"))
        self.assertTrue(pm.hasAttr(instance.pynode, "characterName"))
        self.assertTrue(pm.hasAttr(instance.pynode, "rootCtl"))
        self.assertTrue(pm.hasAttr(instance.pynode, "controlRig"))
        self.assertTrue(pm.hasAttr(instance.pynode, "deformationRig"))
        self.assertTrue(pm.hasAttr(instance.pynode, "geometryGroup"))
        self.assertTrue(pm.hasAttr(instance.pynode, "locatorsGroup"))
        self.assertTrue(pm.hasAttr(instance.pynode, "worldLocator"))

        # Instance members
        self.assertEqual(instance.tag, "character")
        self.assertEqual(str(instance.control_rig), instance.CONTROL_RIG_GRP_NAME)
        self.assertEqual(str(instance.deformation_rig), instance.DEFORMATION_RIG_GRP_NAME)
        self.assertEqual(str(instance.geometry_grp), instance.GEOMETRY_GRP_NAME)
        self.assertEqual(str(instance.locators_grp), instance.LOCATORS_GRP_NAME)
        self.assertTrue(pm.objExists(instance.world_locator))

        # Save test scene
        pm.renameFile(self.get_temp_filename("character_component_test_create_default.ma"))
        pm.saveFile(f=1)

    def test_intance_from_meta(self):
        new_character = luna_rig.components.Character.create()
        instance = luna_rig.components.Character(new_character.pynode.name())

        # Assertions
        # Meta node attributes
        self.assertTrue(pm.hasAttr(instance.pynode, "rootCtl"))
        self.assertTrue(pm.hasAttr(instance.pynode, "characterName"))
        self.assertTrue(pm.hasAttr(instance.pynode, "rootCtl"))
        self.assertTrue(pm.hasAttr(instance.pynode, "controlRig"))
        self.assertTrue(pm.hasAttr(instance.pynode, "deformationRig"))
        self.assertTrue(pm.hasAttr(instance.pynode, "geometryGroup"))
        self.assertTrue(pm.hasAttr(instance.pynode, "locatorsGroup"))
        self.assertTrue(pm.hasAttr(instance.pynode, "worldLocator"))

        # Main groups
        self.assertEqual(str(instance.control_rig), instance.CONTROL_RIG_GRP_NAME)
        self.assertEqual(str(instance.deformation_rig), instance.DEFORMATION_RIG_GRP_NAME)
        self.assertEqual(str(instance.geometry_grp), instance.GEOMETRY_GRP_NAME)
        self.assertEqual(str(instance.locators_grp), instance.LOCATORS_GRP_NAME)
        self.assertTrue(pm.objExists(instance.world_locator))

        # Data struct
        self.assertEqual(instance.side, "char")
        self.assertEqual(instance.name, "character")
        self.assertEqual(instance.tag, "character")

        # Save test scene
        pm.renameFile(self.get_temp_filename("character_component_test_instance_from_meta.ma"))
        pm.saveFile(f=1)


if __name__ == "__main__":
    unittest.main(exit=False)
