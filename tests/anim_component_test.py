import pymel.core as pm
import unittest
from Luna.test import TestCase
from Luna_rig.core.component import AnimComponent


class AnimComponentTests(TestCase):
    def setUp(self):
        super(AnimComponentTests, self).setUp()
        pm.newFile(f=1)

    def tearDown(self):
        super(AnimComponentTests, self).tearDown()
        pm.newFile(f=1)

    def test_create_default(self):
        new_component = AnimComponent.create()

        # Assertions
        # Structs
        self.assertEqual(new_component.data.name, "anim_component")
        self.assertEqual(new_component.data.side, "c")

        # Metanode
        self.assertEqual(str(new_component.pynode), "{0}_{1}_00_meta".format(new_component.data.side, new_component.data.name))
        self.assertEqual(new_component.pynode.metaRigType.get(), AnimComponent._type_to_str(AnimComponent))
        self.assertEqual(new_component.pynode.version.get(), 1)
        self.assertEqual(str(new_component.group.root), "{0}_{1}_00_grp".format(new_component.data.side, new_component.data.name))
        self.assertEqual(str(new_component.group.ctls), "{0}_{1}_00_ctls".format(new_component.data.side, new_component.data.name))
        self.assertEqual(str(new_component.group.joints), "{0}_{1}_00_jnts".format(new_component.data.side, new_component.data.name))
        self.assertEqual(str(new_component.group.parts), "{0}_{1}_00_parts".format(new_component.data.side, new_component.data.name))

        # Meta parent attrs on hierarchy
        self.assertTrue(pm.hasAttr(new_component.group.root, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group.ctls, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group.joints, "metaParent"))
        self.assertTrue(pm.hasAttr(new_component.group.parts, "metaParent"))

        # Attributes on meta node
        self.assertTrue(pm.hasAttr(new_component.pynode, "rootGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "ctlsGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "jointsGroup"))
        self.assertTrue(pm.hasAttr(new_component.pynode, "partsGroup"))

        # Connections to metanode
        self.assertTrue(pm.isConnected(new_component.group.root.metaParent, new_component.pynode.rootGroup))
        self.assertTrue(pm.isConnected(new_component.group.ctls.metaParent, new_component.pynode.ctlsGroup))
        self.assertTrue(pm.isConnected(new_component.group.joints.metaParent, new_component.pynode.jointsGroup))
        self.assertTrue(pm.isConnected(new_component.group.parts.metaParent, new_component.pynode.partsGroup))

    def test_create_with_meta_parent(self):
        component1 = AnimComponent.create()
        component2 = AnimComponent.create(meta_parent=component1)

        self.assertTrue(pm.isConnected(component2.pynode.metaParent, component1.pynode.metaChildren[0]))
        self.assertEqual(component2.get_meta_parent(), component1)

    def test_attach_to_component(self):
        component1 = AnimComponent.create()
        component2 = AnimComponent.create()
        component2.attach_to_component(component1)

        # Assertions
        self.assertTrue(pm.isConnected(component2.pynode.metaParent, component1.pynode.metaChildren[0]))
        self.assertEqual(component2.get_meta_parent(), component1)


if __name__ == "__main__":
    unittest.main(exit=False)
