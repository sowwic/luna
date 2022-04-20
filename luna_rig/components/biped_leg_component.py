import luna_rig
from luna import Logger
from luna_rig.components import FKIKComponent
from luna_rig.functions import attrFn
from luna_rig.functions import jointFn
from luna_rig.functions import nameFn


class BipedLegComponent(FKIKComponent):

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=0,
               character=None,
               side="c",
               name="leg",
               start_joint=None,
               end_joint=None,
               ik_world_orient=True,
               default_fkik_state=1,
               foot_roll_axis="y",
               tag="body"):

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

        leg_instance._build_foot(foot_chain, foot_roll_axis=foot_roll_axis)
        return leg_instance

    def _build_foot(self, joint_chain, foot_roll_axis="y"):
        # type: (list[luna_rig.nt.Joint], str) -> None
        """Build reverse foot rig

        Args:
            joint_chain (list[luna_rig.nt.Transform]): list of 3 joints for ankle, foot, toe end.
            foot_roll_axis (str, optional): axis used for foot roll. Defaults to "y".
        """
        # Create control joint chain.
        self.pynode.addAttr("footCtlChain", at="message", multi=1, im=0)
        attrFn.add_meta_attr(joint_chain)
        foot_ctl_chain = jointFn.duplicate_chain(joint_chain, add_name="ctl")
        foot_ctl_chain[0].setParent(self.ctl_chain[-1])
        for jnt in foot_ctl_chain:
            jnt.metaParent.connect(self.pynode.footCtlChain, na=1)

        # Breakdown chain into variables
        ankle_ctl_jnt = self.ctl_chain[-1]
        foot_ctl_jnt, toe_ctl_jnt = foot_ctl_chain

    def create_twist(self, mirrored_chain=False, hip_joints_count=2, shin_joints_count=2, add_hooks=False):
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

    @property
    def foot_ik_chain(self):
        return [joint for joint in self.pynode.footIkChain.listConnections(d=1)]

    @property
    def foot_fk_chain(self):
        return [joint for joint in self.pynode.footFkChain.listConnections(d=1)]

    @property
    def foot_ctl_chain(self):
        return [joint for joint in self.pynode.footCtlChain.listConnections(d=1)]
