import pymel.core as pm
import unittest
from Luna.test import TestCase
from Luna_rig.core.component import AnimComponent


class AnimComponentTests(TestCase):
    def setUp(self):
        pm.newFile(f=1)

    def tearDown(self):
        pm.newFile(f=1)

    def test_create_default(self):
        new_component = AnimComponent.create()

        # Assertions
        # Metanode
        self.assertEqual(str(new_component.pynode), "{0}_{1}_00_meta".format(new_component.side, new_component.name))
        self.assertEqual(new_component.pynode.metaRigType.get(), AnimComponent.as_str())
        self.assertEqual(new_component.pynode.version.get(), 1)
        self.assertEqual(str(new_component.root), "{0}_{1}_00_comp".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_ctls), "{0}_{1}_00_ctls".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_joints), "{0}_{1}_00_jnts".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_parts), "{0}_{1}_00_parts".format(new_component.side, new_component.name))

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
        component1 = AnimComponent.create()
        component2 = AnimComponent.create(meta_parent=component1)

        self.assertTrue(pm.isConnected(component2.pynode.metaParent, component1.pynode.metaChildren[0]))
        self.assertEqual(component2.get_meta_parent(), component1)

        # Save test scene
        pm.renameFile(self.get_temp_filename("anim_component_test_create_with_meta_parent.ma"))
        pm.saveFile(f=1)

    def test_attach_to_component(self):
        component1 = AnimComponent.create()
        component2 = AnimComponent.create()
        component2.attach_to_component(component1)

        # Assertions
        self.assertTrue(pm.isConnected(component2.pynode.metaParent, component1.pynode.metaChildren[0]))
        self.assertEqual(component2.get_meta_parent(), component1)

        # Save test scene
        pm.renameFile(self.get_temp_filename("anim_component_test_attach_to_component.ma"))
        pm.saveFile(f=1)

    def test_get_meta_children(self):
        component1 = AnimComponent.create()
        child_components = []
        for i in range(5):
            child_components.append(AnimComponent.create(meta_parent=component1))

        # Assertions
        for child in child_components:
            self.assertEqual(component1, child.get_meta_parent())
            self.assertEqual(component1.pynode, child.get_meta_parent().pynode)
        self.assertListEqual(child_components, component1.get_meta_children())
        self.assertListEqual(child_components, component1.get_meta_children(of_type=AnimComponent))

        # Save test scene
        pm.renameFile(self.get_temp_filename("anim_component_test_get_meta_children.ma"))
        pm.saveFile(f=1)

    def test_instance_from_meta(self):
        component1 = AnimComponent.create()
        new_component = AnimComponent(component1.pynode.name())

        # Assertions
        # Structs
        self.assertEqual(new_component.name, "anim_component")
        self.assertEqual(new_component.side, "c")

        # Metanode
        self.assertEqual(str(new_component.pynode), "{0}_{1}_00_meta".format(new_component.side, new_component.name))
        self.assertEqual(new_component.pynode.metaRigType.get(), AnimComponent.as_str())
        self.assertEqual(new_component.pynode.version.get(), 1)
        self.assertEqual(str(new_component.root), "{0}_{1}_00_comp".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_ctls), "{0}_{1}_00_ctls".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_joints), "{0}_{1}_00_jnts".format(new_component.side, new_component.name))
        self.assertEqual(str(new_component.group_parts), "{0}_{1}_00_parts".format(new_component.side, new_component.name))

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
