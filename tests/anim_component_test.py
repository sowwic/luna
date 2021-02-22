import pymel.core as pm
import unittest
from luna.test import TestCase
import luna_rig


class AnimComponentTests(TestCase):
    def setUp(self):
        pm.newFile(f=1)

    def tearDown(self):
        pm.newFile(f=1)

    def test_create_default(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        new_component = luna_rig.AnimComponent.create(character=test_character)

        # Assertions
        # Metanode
        self.assertEqual(str(new_component.pynode), "{0}_{1}_00_meta".format(new_component.side, new_component.name))
        self.assertEqual(new_component.pynode.metaType.get(), luna_rig.AnimComponent.as_str())
        self.assertEqual(str(new_component.root), "{0}_{1}_00_comp".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_ctls), "{0}_{1}_00_ctls".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_joints), "{0}_{1}_00_jnts".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_parts), "{0}_{1}_00_parts".format(new_component.side, new_component.name))

        # Character connection
        self.assertEqual(new_component.character, test_character)

        # Meta parent attrs on hierarchy
        self.assertTrue(pm.hasAttr(new_component.root, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group_ctls, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group_joints, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group_parts, "metaParent"))

        # Attributes on meta node
        self.assertTrue(pm.hasAttr(new_component.pynode, "rootGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "ctlsGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "jointsGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "partsGroup"))

        # Connections to metanode
        self.assertTrue(pm.isConnected(new_component.root.metaParent, new_component.pynode.rootGroup))
        self.assertTrue(pm.isConnected(new_component.group_ctls.metaParent, new_component.pynode.ctlsGroup))
        self.assertTrue(pm.isConnected(new_component.group_joints.metaParent, new_component.pynode.jointsGroup))
        self.assertTrue(pm.isConnected(new_component.group_parts.metaParent, new_component.pynode.partsGroup))

        # Name, side
        self.assertEqual(new_component.name, "anim_component")
        self.assertEqual(new_component.side, "c")

        # Save test scene
        pm.renameFile(self.get_temp_filename("anim_component_test_create_default.ma"))
        pm.saveFile(f=1)

    def test_create_with_meta_parent(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        component1 = luna_rig.AnimComponent.create(character=test_character)
        component2 = luna_rig.AnimComponent.create(meta_parent=component1, character=test_character)

        self.assertTrue(pm.isConnected(component2.pynode.metaParent, component1.pynode.metaChildren[0]))
        self.assertEqual(component2.meta_parent, component1)

        # Save test scene
        pm.renameFile(self.get_temp_filename("anim_component_test_create_with_meta_parent.ma"))
        pm.saveFile(f=1)

    def test_attach_to_component(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        component1 = luna_rig.AnimComponent.create(character=test_character)
        component2 = luna_rig.AnimComponent.create(character=test_character)
        component2.attach_to_component(component1)

        # Assertions
        self.assertTrue(pm.isConnected(component2.pynode.metaParent, component1.pynode.metaChildren[0]))
        self.assertEqual(component2.meta_parent, component1)

        # Save test scene
        pm.renameFile(self.get_temp_filename("anim_component_test_attach_to_component.ma"))
        pm.saveFile(f=1)

    def test_get_meta_children(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        component1 = luna_rig.AnimComponent.create(character=test_character)
        child_components = []
        for i in range(5):
            child_components.append(luna_rig.AnimComponent.create(meta_parent=component1, character=test_character))

        # Assertions
        for child in child_components:
            self.assertEqual(component1, child.meta_parent)
            self.assertEqual(component1.pynode, child.meta_parent.pynode)
            self.assertEqual(component1.character, child.character)
        self.assertListEqual(child_components, component1.get_meta_children())
        self.assertListEqual(child_components, component1.get_meta_children(of_type=luna_rig.AnimComponent))

        # Save test scene
        pm.renameFile(self.get_temp_filename("anim_component_test_get_meta_children.ma"))
        pm.saveFile(f=1)

    def test_instance_from_meta(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        component1 = luna_rig.AnimComponent.create(character=test_character)
        new_component = luna_rig.AnimComponent(component1.pynode.name())

        # Assertions
        # Structs
        self.assertEqual(new_component.name, "anim_component")
        self.assertEqual(new_component.side, "c")

        # Metanode
        self.assertEqual(str(new_component.pynode), "{0}_{1}_00_meta".format(new_component.side, new_component.name))
        self.assertEqual(new_component.pynode.metaType.get(), luna_rig.AnimComponent.as_str())
        self.assertEqual(str(new_component.root), "{0}_{1}_00_comp".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_ctls), "{0}_{1}_00_ctls".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_joints), "{0}_{1}_00_jnts".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_parts), "{0}_{1}_00_parts".format(new_component.side, new_component.name))

        # Character connections
        self.assertEqual(new_component.character, test_character)

        # Meta parent attrs on hierarchy
        self.assertTrue(pm.hasAttr(new_component.root, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group_ctls, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group_joints, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group_parts, "metaParent"))

        # Attributes on meta node
        self.assertTrue(pm.hasAttr(new_component.pynode, "rootGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "ctlsGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "jointsGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "partsGroup"))

        # Connections to metanode
        self.assertTrue(pm.isConnected(new_component.root.metaParent, new_component.pynode.rootGroup))
        self.assertTrue(pm.isConnected(new_component.group_ctls.metaParent, new_component.pynode.ctlsGroup))
        self.assertTrue(pm.isConnected(new_component.group_joints.metaParent, new_component.pynode.jointsGroup))
        self.assertTrue(pm.isConnected(new_component.group_parts.metaParent, new_component.pynode.partsGroup))

        # Save test scene
        pm.renameFile(self.get_temp_filename("anim_component_test_instance_from_meta.ma"))
        pm.saveFile(f=1)


if __name__ == "__main__":
    unittest.main(exit=False)
