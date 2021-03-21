# Python biped build


```python
import pymel.core as pm
from luna import Logger
import luna_rig
from luna_rig.core import pybuild
from luna_rig import importexport


class RigBuild(pybuild.PyBuild):
    def run(self):
        importexport.BlendShapeManager().import_all()

        self.spine = luna_rig.components.FKIKSpineComponent.create(side="c",
                                                                   name="spine",
                                                                   start_joint="c_spine_00_jnt",
                                                                   end_joint="c_spine_02_jnt")
        self.left_leg = luna_rig.components.FKIKComponent.create(side="l",
                                                                 name="leg",
                                                                 start_joint="l_leg_00_jnt",
                                                                 end_joint="l_leg_02_jnt",
                                                                 ik_world_orient=True,
                                                                 meta_parent=self.spine,
                                                                 hook=self.spine.Hooks.HIPS)
        self.right_leg = luna_rig.components.FKIKComponent.create(side="r",
                                                                  name="leg",
                                                                  start_joint="r_leg_00_jnt",
                                                                  end_joint="r_leg_02_jnt",
                                                                  ik_world_orient=True,
                                                                  meta_parent=self.spine,
                                                                  hook=self.spine.Hooks.HIPS)
        self.left_clavicle = luna_rig.components.FKComponent.create(side="l",
                                                                    name="clavicle",
                                                                    start_joint="l_clavicle_00_jnt",
                                                                    end_joint="l_clavicle_00_jnt",
                                                                    add_end_ctl=True,
                                                                    meta_parent=self.spine,
                                                                    hook=self.spine.Hooks.CHEST)
        self.right_clavicle = luna_rig.components.FKComponent.create(side="r",
                                                                     name="clavicle",
                                                                     start_joint="r_clavicle_00_jnt",
                                                                     end_joint="r_clavicle_00_jnt",
                                                                     add_end_ctl=True,
                                                                     meta_parent=self.spine,
                                                                     hook=self.spine.Hooks.CHEST)
        self.left_arm = luna_rig.components.FKIKComponent.create(side="l",
                                                                 name="arm",
                                                                 start_joint="l_shoulder_00_jnt",
                                                                 end_joint="l_wrist_00_jnt",
                                                                 meta_parent=self.left_clavicle,
                                                                 hook=0)
        self.right_arm = luna_rig.components.FKIKComponent.create(side="r",
                                                                  name="arm",
                                                                  start_joint="r_shoulder_00_jnt",
                                                                  end_joint="r_wrist_00_jnt",
                                                                  meta_parent=self.right_clavicle,
                                                                  hook=0)
        self.head = luna_rig.components.FKComponent.create(side="c",
                                                           name="head",
                                                           start_joint="c_neck_00_jnt",
                                                           end_joint="c_head_01_jnt",
                                                           add_end_ctl=False,
                                                           meta_parent=self.spine,
                                                           hook=self.spine.Hooks.CHEST)
        self.left_foot = luna_rig.components.FootComponent.create(meta_parent=self.left_leg,
                                                                  start_joint="l_foot_00_jnt",
                                                                  end_joint="l_foot_01_jnt",
                                                                  rv_chain="l_foot_rv_00_jnt",
                                                                  foot_locators_grp="l_foot_roll_grp")
        self.right_foot = luna_rig.components.FootComponent.create(meta_parent=self.right_leg,
                                                                   start_joint="r_foot_00_jnt",
                                                                   end_joint="r_foot_01_jnt",
                                                                   rv_chain="r_foot_rv_00_jnt",
                                                                   foot_locators_grp="r_foot_roll_grp")

        # Twist components
        self.left_arm_upper_twist = luna_rig.components.TwistComponent.create(self.left_arm,
                                                                              name="upper_twist",
                                                                              start_joint=self.left_arm.ctl_chain[0],
                                                                              end_joint=self.left_arm.ctl_chain[1],
                                                                              num_joints=2,
                                                                              start_object=self.left_arm.in_hook.transform,
                                                                              mirrored_chain=False)
        self.left_arm_lower_twist = luna_rig.components.TwistComponent.create(self.left_arm,
                                                                              name="lower_twist",
                                                                              start_joint=self.left_arm.ctl_chain[1],
                                                                              end_joint=self.left_arm.ctl_chain[2],
                                                                              num_joints=2,
                                                                              mirrored_chain=False)
        self.right_arm_upper_twist = luna_rig.components.TwistComponent.create(self.right_arm,
                                                                               name="upper_twist",
                                                                               start_joint=self.right_arm.ctl_chain[0],
                                                                               end_joint=self.right_arm.ctl_chain[1],
                                                                               num_joints=2,
                                                                               start_object=self.right_arm.in_hook.transform,
                                                                               mirrored_chain=True)
        self.right_arm_lower_twist = luna_rig.components.TwistComponent.create(self.right_arm,
                                                                               name="lower_twist",
                                                                               start_joint=self.right_arm.ctl_chain[1],
                                                                               end_joint=self.right_arm.ctl_chain[2],
                                                                               num_joints=2,
                                                                               mirrored_chain=True)
        self.left_leg_upper_twist = luna_rig.components.TwistComponent.create(self.left_leg,
                                                                              name="upper_twist",
                                                                              start_joint=self.left_leg.ctl_chain[0],
                                                                              end_joint=self.left_leg.ctl_chain[1],
                                                                              num_joints=2,
                                                                              start_object=self.left_leg.in_hook.transform,
                                                                              mirrored_chain=False)
        self.left_leg_lower_twist = luna_rig.components.TwistComponent.create(self.left_leg,
                                                                              name="lower_twist",
                                                                              start_joint=self.left_leg.ctl_chain[1],
                                                                              end_joint=self.left_leg.ctl_chain[2],
                                                                              num_joints=2,
                                                                              mirrored_chain=False)
        self.right_leg_upper_twist = luna_rig.components.TwistComponent.create(self.right_leg,
                                                                               name="upper_twist",
                                                                               start_joint=self.right_leg.ctl_chain[0],
                                                                               end_joint=self.right_leg.ctl_chain[1],
                                                                               num_joints=2,
                                                                               start_object=self.right_leg.in_hook.transform,
                                                                               mirrored_chain=True)
        self.right_leg_lower_twist = luna_rig.components.TwistComponent.create(self.right_leg,
                                                                               name="lower_twist",
                                                                               start_joint=self.right_leg.ctl_chain[1],
                                                                               end_joint=self.right_leg.ctl_chain[2],
                                                                               num_joints=2,
                                                                               mirrored_chain=True)
        # Connect root motion to spine
        self.character.add_root_motion(self.spine.root_control.transform, root_joint="c_root_00_jnt")

        # Adjust hand param control shape
        self.left_arm.param_control.shape = "hand"
        self.left_arm.param_control.mirror_shape_to_opposite(behaviour=False, flip=True)

        # Features
        self.left_clavicle.add_auto_aim(self.left_arm.ik_control)
        self.right_clavicle.add_auto_aim(self.right_arm.ik_control, mirrored_chain=True)
        self.left_arm.fk_controls[0].add_orient_switch(self.character.world_locator, self.left_clavicle.controls[-1])
        self.right_arm.fk_controls[0].add_orient_switch(self.character.world_locator, self.right_clavicle.controls[-1])
        self.head.controls[-1].add_orient_switch(self.character.world_locator, self.head.controls[-2])

        # Parent skeleton hierachy under character group
        self.character.root_motion.setParent(self.character.deformation_rig)
        # Connect components
        for comp in self.character.get_meta_children(of_type=luna_rig.AnimComponent):
            comp.attach_to_skeleton()

    def post(self):
        # Add spaces
        self.left_leg.pv_control.add_world_space()
        self.left_leg.pv_control.add_space(self.left_leg.ik_control, "IK")
        self.right_leg.pv_control.add_world_space()
        self.right_leg.pv_control.add_space(self.right_leg.ik_control, "IK")
        self.left_arm.pv_control.add_world_space()
        self.left_arm.pv_control.add_space(self.left_arm.ik_control, "IK")
        self.right_arm.pv_control.add_world_space()
        self.right_arm.pv_control.add_space(self.right_arm.ik_control, "IK")
        self.left_arm.ik_control.add_world_space()
        self.left_arm.ik_control.add_space(self.head.controls[-1], "Head")
        self.left_arm.pv_control.add_space(self.head.controls[-1], "Head")
        self.right_arm.ik_control.add_world_space()
        self.right_arm.ik_control.add_space(self.head.controls[-1], "Head")
        self.right_arm.pv_control.add_space(self.head.controls[-1], "Head")

        # Import data
        importexport.CtlShapeManager().import_asset_shapes()
        importexport.DrivenPoseManager().import_all()
        importexport.SkinManager().import_all()
        importexport.NgLayersManager().import_all()

        # Create sets, lock geometry, skel selection
        self.character.set_publish_mode(False)


if __name__ == "__main__":
    RigBuild("character", "Dummy")
```
## Build results
---
### Rig:
![biped_rig](/docs/biped_rig.png)

### Node graph:
![biped_graph](/docs/biped_graph.png)
