import pymel.core as pm
import unittest

from Luna import Logger
from Luna.test import TestCase
from Luna.static import names
from Luna_rig import components
reload(components)


class CharacterTests(TestCase):
    def setUp(self):
        super(CharacterTests, self).setUp()
        pm.newFile(f=1)

    def tearDown(self):
        pm.renameFile(self.get_temp_filename("character_component_test.ma"))
        pm.saveFile(f=1)
        super(CharacterTests, self).tearDown()
        pm.newFile(f=1)

    def test_create_default(self):
        new_character = components.Character.create()
        instance = components.Character(new_character.pynode.name())

        # Assertions
        self.assertTrue(pm.hasAttr(new_character.pynode, "rootCtl"))
        self.assertEqual(str(instance.hierarchy.control_rig), names.Character.control_rig.value)
        self.assertEqual(str(instance.hierarchy.deformation_rig), names.Character.deformation_rig.value)
        self.assertEqual(str(instance.hierarchy.geometry_grp), names.Character.geometry.value)
        self.assertEqual(str(instance.hierarchy.locators_grp), names.Character.locators.value)


if __name__ == "__main__":
    unittest.main(exit=False)
