import pymel.core as pm
import luna_rig
from luna import Logger
from luna_rig.components import FKIKComponent
from luna_rig.functions import attrFn
from luna_rig.functions import jointFn


class BipedLegComponent(FKIKComponent):

    ROLL_ATTRS = ["footRoll", "toeRoll", "heelRoll", "bank", "heelTwist", "toeTwist", "toeTap"]
    FOOT_CLASS = luna_rig.components.FootComponent

    @classmethod
    def create(cls,
               start_joint,
               meta_parent=None,
               hook=0,
               character=None,
               side="c",
               name="leg",
               end_joint=None,
               tag="body",
               ik_world_orient=True,
               default_fkik_state=1):

        full_input_chain = jointFn.joint_chain(start_joint, end_joint)
        if not len(full_input_chain) == 5:
            Logger.error("{0}: joint chain must be of length 5. Got {1}".format(
                cls.as_str(name_only=True), full_input_chain))
            raise ValueError("Invalid joint chain length.")

        leg_chain = full_input_chain[:3]
        foot_chain = full_input_chain[3:]

        leg_instance = super(BipedLegComponent, cls).create(meta_parent=meta_parent,
                                                            hook=hook,
                                                            character=character,
                                                            side=side,
                                                            name=name,
                                                            start_joint=leg_chain[0],
                                                            end_joint=leg_chain[-1],
                                                            ik_world_orient=ik_world_orient,
                                                            default_state=default_fkik_state,
                                                            param_locator=None,
                                                            tag=tag)  # type: BipedLegComponent

        attrFn.add_meta_attr(foot_chain)
        leg_instance._store_bind_joints(foot_chain)
        return leg_instance

    def build_foot(self, reverse_chain, foot_locators_grp, foot_roll_axis="ry"):
        # type: (luna_rig.nt.Joint | str, str, str) -> None
        """Build reverse foot rig

        Args:
            joint_chain (list[luna_rig.nt.Transform]): list of 3 joints for ankle, foot, toe end.
            foot_roll_axis (str, optional): axis used for foot roll. Defaults to "y".
        """
        # Create control joint chain.
        foot = self.FOOT_CLASS.create(self,
                                      start_joint=self.bind_joints[3],
                                      end_joint=self.bind_joints[4],
                                      rv_chain=reverse_chain,
                                      foot_locators_grp=foot_locators_grp,
                                      roll_axis=foot_roll_axis,
                                      tag=self.tag)
        return foot

    def create_twist(self, hip_joints_count=2, shin_joints_count=2,  mirrored_chain=False,  add_hooks=False):
        upper_twist = luna_rig.components.TwistComponent.create(self,
                                                                name="upper_twist",
                                                                start_joint=self.ctl_chain[0],
                                                                end_joint=self.ctl_chain[1],
                                                                start_object=self.in_hook.transform,
                                                                mirrored_chain=mirrored_chain,
                                                                num_joints=hip_joints_count,
                                                                add_hooks=add_hooks,
                                                                tag=self.tag)  # type: luna_rig.components.TwistComponent

        lower_twist = luna_rig.components.TwistComponent.create(self,
                                                                name="lower_twist",
                                                                start_joint=self.ctl_chain[1],
                                                                end_joint=self.ctl_chain[2],
                                                                mirrored_chain=mirrored_chain,
                                                                num_joints=shin_joints_count,
                                                                add_hooks=add_hooks,
                                                                tag=self.tag)  # type: luna_rig.components.TwistComponent
        return upper_twist, lower_twist

    def get_foot(self):
        # type: () -> luna_rig.components.FootComponent | None
        return next(iter([self.get_meta_children(of_type=luna_rig.components.FootComponent)]), None)
