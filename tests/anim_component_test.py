import unittest

from maya import cmds

import luna_rig
from luna.test import TestCase


class AnimComponentTests(TestCase):
    def setUp(self):
        cmds.file(newFile=True, force=True)

    def tearDown(self):
        cmds.file(newFile=True, force=True)

    def test_create_default(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        new_component = luna_rig.AnimComponent.create(character=test_character)

        # Assertions
        # Metanode
        self.assertEqual(
            str(new_component.pynode),
            f"{new_component.side}_{new_component.name}_00_meta",
        )
        self.assertEqual(
            new_component.pynode.metaType.get(), luna_rig.AnimComponent.as_str()
        )
        self.assertEqual(
            str(new_component.root),
            f"{new_component.side}_{new_component.name}_00_comp",
        )
        self.assertEqual(
            str(new_component.group_ctls),
            f"{new_component.side}_{new_component.name}_00_ctls",
        )
        self.assertEqual(
            str(new_component.group_joints),
            f"{new_component.side}_{new_component.name}_00_jnts",
        )
        self.assertEqual(
            str(new_component.group_parts),
            f"{new_component.side}_{new_component.name}_00_parts",
        )
        self.assertEqual(
            str(new_component.group_noscale),
            f"{new_component.side}_{new_component.name}_00_noscale",
        )
        self.assertEqual(
            str(new_component.group_out),
            f"{new_component.side}_{new_component.name}_00_out",
        )
        self.assertEqual(new_component.tag, "")

        # Character connection
        self.assertEqual(new_component.character, test_character)

        # Meta parent attrs on hierarchy
        self.assertTrue(cmds.objExists(f"{new_component.root}.metaParent"))
        self.assertTrue(cmds.objExists(f"{new_component.group_ctrls}.metaParent"))
        self.assertTrue(cmds.objExists(f"{new_component.group_joints}.metaParent"))
        self.assertTrue(cmds.objExists(f"{new_component.group_parts}.metaParent"))
        self.assertTrue(cmds.objExists(f"{new_component.group_out}.metaParent"))
        self.assertTrue(cmds.objExists(f"{new_component.group_noscale}.metaParent"))

        # Attributes on meta node
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.rootGroup"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.jointsGroup"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.partsGroup"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.noScaleGroup"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.outGroup"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.outHooks"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.inHook"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.bindJoints"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.ctlChain"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.control"))

        # Connections to metanode
        self.assertTrue(
            cmds.isConnected(
                new_component.root.metaParent, new_component.pynode.rootGroup
            )
        )
        self.assertTrue(
            cmds.isConnected(
                new_component.group_ctls.metaParent, new_component.pynode.ctlsGroup
            )
        )
        self.assertTrue(
            cmds.isConnected(
                new_component.group_joints.metaParent, new_component.pynode.jointsGroup
            )
        )
        self.assertTrue(
            cmds.isConnected(
                new_component.group_parts.metaParent, new_component.pynode.partsGroup
            )
        )
        self.assertTrue(
            cmds.isConnected(
                new_component.group_out.metaParent, new_component.pynode.outGroup
            )
        )
        self.assertTrue(
            cmds.isConnected(
                new_component.group_noscale.metaParent, new_component.pynode.noScaleGroup
            )
        )

        # Name, side
        self.assertEqual(new_component.name, "anim_component")
        self.assertEqual(new_component.side, "c")

        # Save test scene
        cmds.file(rename=self.get_temp_filename("anim_component_test_create_default.ma"))
        cmds.file(save=True, force=True)

    def test_create_with_meta_parent(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        component1 = luna_rig.AnimComponent.create(character=test_character)
        component2 = luna_rig.AnimComponent.create(
            meta_parent=component1, character=test_character
        )

        self.assertTrue(
            cmds.isConnected(
                component2.pynode.metaParent, component1.pynode.metaChildren[0]
            )
        )
        self.assertEqual(component2.meta_parent, component1)

        # Save test scene
        cmds.file(
            rename=self.get_temp_filename(
                "anim_component_test_create_with_meta_parent.ma"
            )
        )
        cmds.file(save=True, force=True)

    def test_attach_to_component(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        component1 = luna_rig.AnimComponent.create(character=test_character)
        component2 = luna_rig.AnimComponent.create(character=test_character)
        component2.attach_to_component(component1)

        # Assertions
        self.assertTrue(
            cmds.isConnected(
                component2.pynode.metaParent, component1.pynode.metaChildren[0]
            )
        )
        self.assertEqual(component2.meta_parent, component1)
        self.assertIsNone(component2.in_hook)

        # Save test scene
        cmds.file(
            rename=self.get_temp_filename("anim_component_test_attach_to_component.ma"),
            force=True,
        )
        cmds.saveFile(f=1)

    def test_get_meta_children(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        component1 = luna_rig.AnimComponent.create(character=test_character)
        child_components = []
        for i in range(5):
            child_components.append(
                luna_rig.AnimComponent.create(
                    meta_parent=component1, character=test_character
                )
            )

        # Assertions
        for child in child_components:
            self.assertEqual(component1, child.meta_parent)
            self.assertEqual(component1.pynode, child.meta_parent.pynode)
            self.assertEqual(component1.character, child.character)
        self.assertListEqual(child_components, component1.get_meta_children())
        self.assertListEqual(
            child_components,
            component1.get_meta_children(of_type=luna_rig.AnimComponent),
        )

        # Save test scene
        cmds.file(
            rename=self.get_temp_filename("anim_component_test_get_meta_children.ma"),
            force=True,
        )
        cmds.file(save=True, force=True)

    def test_instance_from_meta(self):
        test_character = luna_rig.components.Character.create(name="test_character")
        component1 = luna_rig.AnimComponent.create(character=test_character)
        new_component = luna_rig.AnimComponent(component1.pynode.name())

        # Assertions
        # Structs
        self.assertEqual(new_component.name, "anim_component")
        self.assertEqual(new_component.side, "c")

        # Metanode
        self.assertEqual(
            str(new_component.pynode),
            f"{new_component.side}_{new_component.name}_00_meta",
        )
        self.assertEqual(
            new_component.pynode.metaType.get(), luna_rig.AnimComponent.as_str()
        )
        self.assertEqual(
            str(new_component.root),
            f"{new_component.side}_{new_component.name}_00_comp",
        )
        self.assertEqual(
            str(new_component.group_ctls),
            f"{new_component.side}_{new_component.name}_00_ctls",
        )
        self.assertEqual(
            str(new_component.group_joints),
            f"{new_component.side}_{new_component.name}_00_jnts",
        )
        self.assertEqual(
            str(new_component.group_parts),
            f"{new_component.side}_{new_component.name}_00_parts",
        )

        # Character connections
        self.assertEqual(new_component.character, test_character)

        # Meta parent attrs on hierarchy
        self.assertTrue(cmds.objExists(f"{new_component.root}.metaParent"))
        self.assertTrue(cmds.objExists(f"{new_component.group_ctls}.metaParent"))
        self.assertTrue(cmds.objExists(f"{new_component.group_joints}.metaParent"))
        self.assertTrue(cmds.objExists(f"{new_component.group_parts}.metaParent"))

        # Attributes on meta node
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.rootGroup"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.ctlsGroup"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.jointsGroup"))
        self.assertTrue(cmds.objExists(f"{new_component.pynode}.partsGroup"))

        # Connections to metanode
        self.assertTrue(
            cmds.isConnected(
                new_component.root.metaParent, new_component.pynode.rootGroup
            )
        )
        self.assertTrue(
            cmds.isConnected(
                new_component.group_ctls.metaParent, new_component.pynode.ctlsGroup
            )
        )
        self.assertTrue(
            cmds.isConnected(
                new_component.group_joints.metaParent, new_component.pynode.jointsGroup
            )
        )
        self.assertTrue(
            cmds.isConnected(
                new_component.group_parts.metaParent, new_component.pynode.partsGroup
            )
        )

        # Save test scene
        cmds.file(
            rename=self.get_temp_filename("anim_component_test_instance_from_meta.ma"),
            force=True,
        )
        cmds.file(save=True, force=True)


if __name__ == "__main__":
    unittest.main(exit=False)
