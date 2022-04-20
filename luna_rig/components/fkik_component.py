import pymel.core as pm
from luna import Logger
from luna.utils import enumFn
import luna_rig
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.rigFn as rigFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.animFn as animFn
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.functions.transformFn as transformFn


class FKIKComponent(luna_rig.AnimComponent):

    class Hooks(enumFn.Enum):
        START_JNT = 0
        END_JNT = 1

    @property
    def ik_control(self):
        transform = self.pynode.ikControl.get()  # type: luna_rig.nt.Transform
        return luna_rig.Control(transform)

    @property
    def pv_control(self):
        transform = self.pynode.poleVectorControl.get()  # type: luna_rig.nt.Transform
        return luna_rig.Control(transform)

    @property
    def fk_controls(self):
        return [luna_rig.Control(node) for node in self.pynode.fkControls.listConnections(d=1)]

    @property
    def param_control(self):
        transform = self.pynode.paramControl.get()
        return luna_rig.Control(transform)

    @property
    def handle(self):
        node = self.pynode.ikHandle.get()  # type:luna_rig.nt.IkHandle
        return node

    @property
    def matching_helper(self):
        transform = self.pynode.matchingHelper.get()  # type: luna_rig.nt.Transform
        return transform

    @property
    def group_joints_offset(self):
        transform = self.pynode.jointOffsetGrp.get()  # type: luna_rig.nt.Transform
        return transform

    @property
    def fkik_state(self):
        state = self.param_control.transform.fkik.get()  # type: float
        return state

    @fkik_state.setter
    def fkik_state(self, value):
        self.param_control.transform.fkik.set(value)

    @property
    def actions_dict(self):
        actions = super(FKIKComponent, self).actions_dict
        actions = {"Switch FKIK": {"callback": self.switch_fkik,
                                   "icon": "switch.png"}}
        return actions

    # ========= Getter methods ========== #
    def get_ik_control(self):
        return self.ik_control

    def get_pv_control(self):
        return self.pv_control

    def get_fk_controls(self):
        return self.fk_controls

    def get_param_control(self):
        return self.param_control

    def get_handle(self):
        return self.handle

    def get_matching_helper(self):
        return self.matching_helper

    def get_fkik_state(self):
        return self.fkik_state

    def get_fk_control_at(self, index):
        return self.fk_controls[int(index)]

    def set_fkik_state(self, value):
        self.fkik_state = value

    def get_start_hook_index(self):
        return self.Hooks.START_JNT.value

    def get_end_hook_index(self):
        return self.Hooks.END_JNT.value

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=0,
               character=None,
               side="c",
               name="fkik_component",
               start_joint=None,
               end_joint=None,
               ik_world_orient=False,
               default_state=1,
               param_locator=None,
               tag=""):
        # Create instance and add attrs
        instance = super(FKIKComponent, cls).create(meta_parent=meta_parent, side=side,
                                                    name=name, character=character, tag=tag)  # type: FKIKComponent
        instance.pynode.addAttr("fkControls", at="message", multi=1, im=0)
        instance.pynode.addAttr("ikControl", at="message")
        instance.pynode.addAttr("poleVectorControl", at="message")
        instance.pynode.addAttr("paramControl", at="message")
        instance.pynode.addAttr("matchingHelper", at="message")
        instance.pynode.addAttr("jointOffsetGrp", at="message")
        instance.pynode.addAttr("ikHandle", at="message")
        # Joint chain
        joint_chain = jointFn.joint_chain(start_joint, end_joint)
        jointFn.validate_rotations(joint_chain)

        # Create control chain
        for jnt in joint_chain:
            attrFn.add_meta_attr(jnt)
        ctl_chain = jointFn.duplicate_chain(
            original_chain=joint_chain, add_name="ctl", new_parent=instance.group_joints)
        jnt_offset_grp = nodeFn.create(
            "transform", [instance.indexed_name, "constr"], instance.side, suffix="grp", p=instance.group_joints)
        attrFn.add_meta_attr(jnt_offset_grp)
        pm.matchTransform(jnt_offset_grp, ctl_chain[0])
        ctl_chain[0].setParent(jnt_offset_grp)

        # Create FK setup
        fk_controls = []
        next_parent = instance.group_ctls
        for ctl_jnt in ctl_chain:
            fk_ctl = luna_rig.Control.create(side=instance.side,
                                             name="{0}_fk".format(instance.indexed_name),
                                             guide=ctl_jnt,
                                             attributes="r",
                                             parent=next_parent,
                                             shape="circleCrossed",
                                             tag="fk")
            next_parent = fk_ctl
            fk_controls.append(fk_ctl)
        for fk_ctl, ctl_jnt in zip(fk_controls[:-1], ctl_chain):
            pm.orientConstraint(fk_ctl.transform, ctl_jnt)

        # Create IK setup
        ik_control = luna_rig.Control.create(side=instance.side,
                                             name="{0}_ik".format(instance.indexed_name),
                                             guide=ctl_chain[-1],
                                             delete_guide=False,
                                             attributes="tr",
                                             parent=instance.group_ctls,
                                             shape="cube",
                                             match_orient=not ik_world_orient,
                                             tag="ik")
        ik_handle = pm.ikHandle(n=nameFn.generate_name(instance.name, side=instance.side, suffix="ikh"),
                                sj=ctl_chain[0],
                                ee=ctl_chain[-1],
                                sol="ikRPsolver")[0]
        attrFn.add_meta_attr(ik_handle)
        pm.parent(ik_handle, ik_control.transform)

        # Matching helper
        matching_helper = pm.createNode("transform",
                                        n=nameFn.generate_name(
                                            [instance.indexed_name, "matching_helper"], side=instance.side, suffix="grp"),
                                        p=ik_control.transform)  # type: luna_rig.nt.Transform
        matching_helper.setParent(fk_controls[-1].transform)
        attrFn.add_meta_attr(matching_helper)

        # Pole vector
        pole_locator = jointFn.get_pole_vector(ctl_chain)
        pv_control = luna_rig.Control.create(side=instance.side,
                                             name="{0}_pvec".format(instance.indexed_name),
                                             guide=pole_locator,
                                             delete_guide=True,
                                             parent=instance.group_ctls,
                                             attributes="tr",
                                             shape="poleVector")
        pm.poleVectorConstraint(pv_control.transform, ik_handle)
        # Add wire
        if len(ctl_chain) % 2:
            wire_source = ctl_chain[(len(ctl_chain) - 1) // 2]
        else:
            wire_source = ctl_chain[len(ctl_chain) // 2]
        pv_control.add_wire(wire_source)

        # Param
        param_control = luna_rig.Control.create(side=instance.side,
                                                name="{0}_param".format(instance.indexed_name),
                                                guide=ctl_chain[-1],
                                                delete_guide=False,
                                                attributes="",
                                                parent=instance.group_ctls,
                                                match_orient=False,
                                                offset_grp=False,
                                                shape="small_cog",
                                                orient_axis="y")

        pm.parentConstraint(ctl_chain[-1], param_control.group, mo=1)

        # Create blend
        param_control.transform.addAttr("fkik", nn="FK/IK", at="float",
                                        min=0.0, max=1.0, dv=default_state, k=True)
        reverse_fkik = pm.createNode("reverse", n=nameFn.generate_name(
            [instance.indexed_name, "fkik"], side=instance.side, suffix="rev"))
        param_control.transform.fkik.connect(reverse_fkik.inputX)
        param_control.transform.fkik.connect(ik_control.group.visibility)
        param_control.transform.fkik.connect(pv_control.group.visibility)
        reverse_fkik.outputX.connect(fk_controls[0].group.visibility)
        param_control.transform.fkik.connect(ik_handle.ikBlend)

        # Add proxy attributes on fk/ik controls
        for ctl in fk_controls + [ik_control, pv_control]:
            ctl.transform.addAttr("fkik", nn="FK/IK", at="float", min=0.0,
                                  max=1.0, dv=default_state, k=True, usedAsProxy=True)
            param_control.transform.fkik.connect(ctl.transform.fkik)

        # End joint orient
        ikfk_orient_offset = nodeFn.create("transform",
                                           [instance.indexed_name, "ikfk_or"],
                                           instance.side,
                                           "grp",
                                           p=fk_controls[-1].transform)
        last_orient_constr = pm.orientConstraint(
            fk_controls[-1].transform, ikfk_orient_offset, ctl_chain[-1], mo=1)  # type:  luna_rig.nt.OrientConstraint
        ikfk_orient_offset.setParent(ik_control.transform)
        reverse_fkik.outputX.connect(last_orient_constr.getWeightAliasList()[0])
        param_control.transform.fkik.connect(last_orient_constr.getWeightAliasList()[1])

        # Store default items
        instance._store_bind_joints(joint_chain)
        instance._store_ctl_chain(ctl_chain)
        instance._store_controls(fk_controls)
        instance._store_controls([ik_control, pv_control, param_control])

        # Store indiviual items
        for fk_ctl in fk_controls:
            fk_ctl.transform.metaParent.connect(instance.pynode.fkControls, na=1)
        ik_control.transform.metaParent.connect(instance.pynode.ikControl)
        matching_helper.metaParent.connect(instance.pynode.matchingHelper)
        jnt_offset_grp.metaParent.connect(instance.pynode.jointOffsetGrp)
        ik_handle.metaParent.connect(instance.pynode.ikHandle)
        pv_control.transform.metaParent.connect(instance.pynode.poleVectorControl)
        param_control.transform.metaParent.connect(instance.pynode.paramControl)

        # Store attach points
        instance.add_hook(ctl_chain[0], "start_jnt")
        instance.add_hook(ctl_chain[-1], "end_jnt")

        # Connect to character, parent
        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent, hook)

        # Scale controls
        scale_dict = {ik_control: 0.8,
                      pv_control: 0.1,
                      param_control: 0.2}
        for ctl in fk_controls:
            scale_dict[ctl] = 0.2
        instance.scale_controls(scale_dict)

        # Move param control shape
        if not param_locator:
            param_locator = rigFn.get_param_ctl_locator(
                instance.side, joint_chain[-1], move_axis="x")
        param_move_vector = transformFn.get_vector(param_control.transform, param_locator)
        param_control.move_shape(param_move_vector)
        pm.delete(param_locator)

        # Store settings
        instance._store_settings(param_control.transform.fkik)

        # House keeping
        ik_handle.visibility.set(0)
        if instance.character:
            instance.group_parts.visibility.set(0)
            instance.group_joints.visibility.set(0)
        return instance

    def attach_to_component(self, other_comp, hook_index=None):
        super(FKIKComponent, self).attach_to_component(other_comp, hook_index)
        if self.in_hook:
            pm.parentConstraint(self.in_hook.transform, self.group_joints_offset, mo=1)
            pm.parentConstraint(self.in_hook.transform, self.fk_controls[0].group, mo=1)

    def hide_last_fk(self):
        self.fk_controls[-1].group.hide()

    def switch_fkik(self, matching=True):
        # If in FK -> match IK to FK and switch to IK
        if not matching:
            self.fkik_state = not self.fkik_state

        else:
            if not self.fkik_state:
                self.match_ik_to_fk()
                self.fkik_state = 1
            else:
                self.match_fk_to_ik()
                self.fkik_state = 0

    def match_ik_to_fk(self):
        pm.matchTransform(self.ik_control.transform, self.matching_helper)
        # Pole vector
        pole_locator = jointFn.get_pole_vector(self.ctl_chain)
        pm.matchTransform(self.pv_control.transform, pole_locator)
        pm.delete(pole_locator)
        pm.select(self.ik_control.transform, r=1)

    def match_fk_to_ik(self):
        for ctl_jnt, fk_ctl in zip(self.ctl_chain, self.fk_controls):
            pm.matchTransform(fk_ctl.transform, ctl_jnt, rot=1)
        pm.select(self.fk_controls[-1].transform, r=1)

    def bake_fkik(self, source="fk", time_range=None, bake_pv=True, step=1):
        Logger.info("{0}: baking {1} to {2} {3}...".format(self, source.upper(),
                    "IK" if source.lower() == "fk" else "FK", time_range))
        if not time_range:
            time_range = animFn.get_playback_range()
        for frame in range(time_range[0], time_range[1] + 1, step):
            pm.setCurrentTime(frame)
            if source == "fk":
                self.fkik_state = 0
                self.switch_fkik(matching=True)
                self.ik_control.transform.translate.setKey()
                self.ik_control.transform.rotate.setKey()
                if bake_pv:
                    self.pv_control.transform.translate.setKey()
            elif source == "ik":
                self.fkik_state = 1
                self.switch_fkik(matching=True)
                for fk_control in self.fk_controls:
                    fk_control.transform.rotate.setKey()
        # Bake children
        for child in self.meta_children:
            if hasattr(child, "bake_fkik"):
                child.bake_fkik(source=source, time_range=time_range, step=step)

    def add_fk_orient_switch(self):
        if not (self.character and self.in_hook):
            Logger.error("Can't add orient attr without character and parent component hook!")
            return
        self.fk_controls[0].add_orient_switch(self.character.world_locator, self.in_hook.transform)
