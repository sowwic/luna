import pymel.core as pm
import unittest

from Luna import Logger
from Luna.test import TestCase
from Luna.static import names
from Luna_rig import components
reload(components)


class CharacterTests(TestCase):
    def setUp(self):
        pm.newFile(f=1)

    def tearDown(self):
        super(CharacterTests, self).tearDown()
        pm.newFile(f=1)

    def test_create_default(self):
        instance = components.Character.create()

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

        # Struct population
        self.assertEqual(str(instance.hierarchy.control_rig), names.Character.control_rig.value)
        self.assertEqual(str(instance.hierarchy.deformation_rig), names.Character.deformation_rig.value)
        self.assertEqual(str(instance.hierarchy.geometry_grp), names.Character.geometry.value)
        self.assertEqual(str(instance.hierarchy.locators_grp), names.Character.locators.value)
        self.assertTrue(pm.objExists(instance.hierarchy.world_loc))

        # Save test scene
        pm.renameFile(self.get_temp_filename("character_component_test_create_default.ma"))
        pm.saveFile(f=1)

    def test_intance_from_meta(self):
        new_character = components.Character.create()
        instance = components.Character(new_character.pynode.name())

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

        # Hierarchy struct
        self.assertEqual(str(instance.hierarchy.control_rig), names.Character.control_rig.value)
        self.assertEqual(str(instance.hierarchy.deformation_rig), names.Character.deformation_rig.value)
        self.assertEqual(str(instance.hierarchy.geometry_grp), names.Character.geometry.value)
        self.assertEqual(str(instance.hierarchy.locators_grp), names.Character.locators.value)
        self.assertTrue(pm.objExists(instance.hierarchy.world_loc))

        # Data struct
        self.assertEqual(instance.data.side, "char")
        self.assertEqual(instance.data.name, "character")

        # Save test scene
        pm.renameFile(self.get_temp_filename("character_component_test_instance_from_meta.ma"))
        pm.saveFile(f=1)


if __name__ == "__main__":
    unittest.main(exit=False)
