import pymel.core as pm
import luna_rig
from luna import Logger
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.transformFn as transformFn


class FKComponent(luna_rig.AnimComponent):

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=0,
               character=None,
               side="c",
               name="fk_component",
               start_joint=None,
               end_joint=None,
               add_end_ctl=True,
               lock_translate=True,
               tag=""):
        instance = super(FKComponent, cls).create(meta_parent=meta_parent, side=side, name=name, character=character, tag=tag)  # type: FKComponent
        # Joint chain
        joint_chain = jointFn.joint_chain(start_joint, end_joint)
        jointFn.validate_rotations(joint_chain)
        for jnt in joint_chain:
            attrFn.add_meta_attr(jnt)
        ctl_chain = jointFn.duplicate_chain(original_chain=joint_chain, add_name="ctl", new_parent=instance.group_joints)

        # Create control
        fk_controls = []
        next_parent = instance.group_ctls
        skel_chain = ctl_chain if add_end_ctl else ctl_chain[:-1]
        free_attrs = "r" if lock_translate else "tr"
        for jnt in skel_chain:
            ctl = luna_rig.Control.create(side=instance.side,
                                          name="{0}_fk".format(instance.indexed_name),
                                          guide=jnt,
                                          parent=next_parent,
                                          attributes=free_attrs,
                                          shape="circleCrossed",
                                          tag="fk")
            pm.parentConstraint(ctl.transform, jnt, mo=1)
            next_parent = ctl
            fk_controls.append(ctl)

        # Store joint chains
        instance._store_bind_joints(joint_chain)
        instance._store_ctl_chain(ctl_chain)
        instance._store_controls(fk_controls)

        # Store attach points
        for each in fk_controls:
            instance.add_hook(each.transform, "fk")

        # Connect to character, parent
        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent, hook)

        # Scale controls
        scale_dict = {}
        for ctl in fk_controls:
            scale_dict[ctl] = 0.2
        instance.scale_controls(scale_dict)

        # House keeping
        if instance.character:
            instance.group_parts.visibility.set(0)
            instance.group_joints.visibility.set(0)
        return instance

    def attach_to_component(self, other_comp, hook_index=0):
        super(FKComponent, self).attach_to_component(other_comp, hook_index=hook_index)
        if self.in_hook:
            pm.parentConstraint(self.in_hook.transform, self.controls[0].group, mo=1)

    def add_auto_aim(self, follow_control, mirrored_chain=False, default_value=5.0):
        if not isinstance(follow_control, luna_rig.Control):
            raise ValueError("{0}: {1} is not a Control instance".format(self, follow_control))
        # Create aim transforms
        aim_grp = pm.createNode("transform", n=nameFn.generate_name([self.indexed_name, "aim"], side=self.side,
                                                                    suffix="grp"), p=self.controls[0].group)  # type: luna_rig.nt.Transform
        no_aim_grp = pm.createNode("transform", n=nameFn.generate_name([self.indexed_name, "noaim"],
                                                                       side=self.side, suffix="grp"), p=self.controls[0].group)  # type: luna_rig.nt.Transform
        constr_grp = pm.createNode("transform", n=nameFn.generate_name([self.indexed_name, "aim_constr"],
                                                                       side=self.side, suffix="grp"), p=self.controls[0].group)  # type: luna_rig.nt.Transform
        target_grp = pm.createNode("transform", n=nameFn.generate_name([self.indexed_name, "target"],
                                                                       side=self.side, suffix="grp"), p=follow_control.transform)  # type: luna_rig.nt.Transform

        # Set aim vector to X or -X
        if mirrored_chain:
            aim_vector = [-1, 0, 0]
        else:
            aim_vector = [1, 0, 0]

        # Create aim setup
        pm.aimConstraint(target_grp, aim_grp, wut="object", wuo=self.controls[0].group, aim=aim_vector)
        pm.delete(pm.aimConstraint(target_grp, no_aim_grp, wut="object", wuo=self.controls[0].group, aim=aim_vector))
        orient_constr = pm.orientConstraint(aim_grp, no_aim_grp, constr_grp)  # type: luna_rig.nt.OrientConstraint
        pm.parent(self.controls[0].offset_list[0], constr_grp)
        # Add attr to control
        self.controls[0].transform.addAttr("autoAim", at="float", dv=default_value, min=0.0, max=10.0, k=1)
        mdl_node = pm.createNode("multDoubleLinear", n=nameFn.generate_name([self.indexed_name, "auto_aim"], side=self.side, suffix="mdl"))
        rev_node = pm.createNode("reverse", n=nameFn.generate_name([self.indexed_name, "auto_aim"], side=self.side, suffix="rev"))
        mdl_node.input2.set(0.1)
        # Attr connections
        self.controls[0].transform.autoAim.connect(mdl_node.input1)
        mdl_node.output.connect(rev_node.inputX)
        mdl_node.output.connect(orient_constr.getWeightAliasList()[0])
        rev_node.outputX.connect(orient_constr.getWeightAliasList()[1])
        # Store settings
        self._store_settings(self.controls[0].transform.autoAim)


class HeadComponent(FKComponent):

    @property
    def head_control(self):
        return self.controls[-1]

    @property
    def neck_controls(self):
        return self.controls[:-1]

    class Hooks:
        HEAD = -1
        NECK_BASE = 0

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=None,
               character=None,
               side="c",
               name="head",
               start_joint=None,
               end_joint=None,
               head_joint_index=-2,
               lock_translate=False,
               tag=""):
        instance = super(HeadComponent, cls).create(meta_parent=meta_parent,
                                                    hook=hook,
                                                    character=character,
                                                    side=side,
                                                    name=name,
                                                    start_joint=start_joint,
                                                    end_joint=end_joint,
                                                    add_end_ctl=head_joint_index == -1,
                                                    lock_translate=lock_translate,
                                                    tag=tag)  # type: HeadComponent
        # Create utility attrib
        instance.pynode.addAttr("headJointIndex", at="long", k=False, dv=head_joint_index)
        instance.pynode.headJointIndex.lock()
        # Adjust head control shape
        head_ctl_move_vector = transformFn.get_vector(instance.ctl_chain[-2], instance.ctl_chain[-1])
        instance.head_control.shape = "circle_pointed"
        scale_dict = {instance.head_control: 0.4}
        instance.scale_controls(scale_dict)
        instance.head_control.move_shape(head_ctl_move_vector)

        return instance

    def get_head_hook_index(self):
        return self.Hooks.HEAD

    def get_neck_base_hook_index(self):
        return self.Hooks.NECK_BASE

    def add_orient_attr(self):
        self.head_control.add_orient_switch(self.character.world_locator, self.neck_controls[-1])
