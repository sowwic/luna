import pymel.core as pm
from luna import Logger
import luna_rig
from luna_rig.functions import jointFn
from luna_rig.functions import attrFn
from luna_rig.functions import nameFn
import luna_rig.functions.animFn as animFn


class FootComponent(luna_rig.AnimComponent):
    ROLL_ATTRS = ["footRoll", "toeRoll", "heelRoll", "bank", "heelTwist", "toeTwist", "toeTap"]

    @property
    def roll_axis(self):
        axis = self.pynode.rollAxis.get()  # type: str
        return axis

    @property
    def fk_control(self):
        return luna_rig.Control(self.pynode.fkControl.listConnections(d=1)[0])

    # ============= Getter methods =============== #
    def get_roll_axis(self):
        return self.roll_axis

    def get_fk_control(self):
        return self.fk_control

    @classmethod
    def create(cls,
               meta_parent=None,
               character=None,
               side=None,
               name="foot",
               start_joint=None,
               end_joint=None,
               rv_chain=None,
               foot_locators_grp=None,
               roll_axis="ry",
               tag="body"):
        # Validate arguments
        if not isinstance(meta_parent, luna_rig.components.FKIKComponent):
            Logger.error("{0}: Invalid meta_parent type. Should be FKIKComponent.")
            raise TypeError
        side = side if side else meta_parent.side
        foot_locators_grp = pm.PyNode(foot_locators_grp)  # type: luna_rig.nt.Transform
        # Create instance and add attrs
        instance = super(FootComponent, cls).create(meta_parent=meta_parent, side=side, name=name, character=character, tag=tag)  # type: FootComponent
        instance.pynode.addAttr("fkChain", at="message", multi=1, im=0)
        instance.pynode.addAttr("ikChain", at="message", multi=1, im=0)
        instance.pynode.addAttr("fkControl", at="message")
        instance.pynode.addAttr("rollAxis", dt="string")
        instance.pynode.rollAxis.set(roll_axis)

        # Chains
        joint_chain = jointFn.joint_chain(start_joint, end_joint)
        for jnt in joint_chain:
            attrFn.add_meta_attr(jnt)
        ctl_chain = jointFn.duplicate_chain(joint_chain, add_name="ctl")
        rv_chain = jointFn.joint_chain(rv_chain)
        ctl_chain[0].setParent(meta_parent.ctl_chain[-1])

        # Foot handles
        ball_handle = pm.ikHandle(n=nameFn.generate_name([instance.indexed_name, "ball"], side=instance.side, suffix="ikh"),
                                  sj=ctl_chain[0].getParent(),
                                  ee=ctl_chain[0],
                                  sol="ikSCsolver")[0]
        toe_handle = pm.ikHandle(n=nameFn.generate_name([instance.indexed_name, "toe"], side=instance.side, suffix="ikh"),
                                 sj=ctl_chain[0],
                                 ee=ctl_chain[1],
                                 sol="ikSCsolver")[0]

        # Foot locators
        for child in foot_locators_grp.getChildren():
            if "inner" in child.name():
                inner_locator = child
            elif "outer" in child.name():
                outer_locator = child
            elif "toe" in child.name():
                toe_locator = child
            elif "heel" in child.name():
                heel_locator = child
        # Tap transform
        toe_tap_transform = pm.createNode("transform", n=nameFn.generate_name([instance.indexed_name, "tap"], side=instance.side, suffix="grp"), p=rv_chain[2])
        toe_tap_transform.setParent(rv_chain[1])
        # Parent handles
        pm.parent(meta_parent.handle, rv_chain[-1])
        ball_handle.setParent(rv_chain[2])
        toe_handle.setParent(toe_tap_transform)

        # Parent foot locators
        foot_locators_grp.setParent(meta_parent.ik_control.transform)
        toe_locator.setParent(heel_locator)
        outer_locator.setParent(toe_locator)
        inner_locator.setParent(outer_locator)
        rv_chain[0].setParent(inner_locator)

        # FK Control
        meta_parent.param_control.transform.fkik.connect(instance.group_ctls.visibility)
        fk_control = luna_rig.Control.create(side=instance.side,
                                             name="{0}_fk".format(instance.indexed_name),
                                             guide=ctl_chain[0],
                                             parent=meta_parent.fk_controls[-1],
                                             delete_guide=False,
                                             attributes="r",
                                             shape="circleCrossed",
                                             tag="fk")
        pm.orientConstraint(fk_control.transform, ctl_chain[0])

        # Fkik blend
        meta_parent.param_control.transform.fkik.connect(ball_handle.ikBlend)
        meta_parent.param_control.transform.fkik.connect(toe_handle.ikBlend)

        # Roll attributes
        attrFn.add_divider(meta_parent.ik_control.transform, attr_name="FOOT")
        for attr_name in FootComponent.ROLL_ATTRS:
            meta_parent.ik_control.transform.addAttr(attr_name, at="float", k=1, dv=0.0)
        meta_parent.ik_control.transform.footRoll.connect(rv_chain[2].attr(roll_axis))
        meta_parent.ik_control.transform.toeRoll.connect(toe_locator.rotateX)
        meta_parent.ik_control.transform.heelRoll.connect(heel_locator.rotateX)
        meta_parent.ik_control.transform.toeTap.connect(toe_tap_transform.attr(roll_axis))
        meta_parent.ik_control.transform.heelTwist.connect(heel_locator.rotateY)
        meta_parent.ik_control.transform.toeTwist.connect(toe_locator.rotateY)
        # Bank logic
        bank_condition = pm.createNode("condition", n=nameFn.generate_name([instance.indexed_name, "bank"], side=instance.side, suffix="cond"))
        if instance.side == "r":
            bank_condition.operation.set(4)
        else:
            bank_condition.operation.set(2)
        bank_condition.colorIfFalseR.set(0)
        meta_parent.ik_control.transform.bank.connect(bank_condition.firstTerm)
        meta_parent.ik_control.transform.bank.connect(bank_condition.colorIfTrueR)
        meta_parent.ik_control.transform.bank.connect(bank_condition.colorIfFalseG)
        bank_condition.outColorG.connect(outer_locator.rotateZ)
        bank_condition.outColorR.connect(inner_locator.rotateZ)

        # Store objects
        instance._store_bind_joints(joint_chain)
        instance._store_ctl_chain(ctl_chain)
        instance._store_controls([fk_control])
        # Store chains
        fk_control.transform.metaParent.connect(instance.pynode.fkControl)

        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent, hook_index=None)

        # Scale controls
        scale_dict = {fk_control: 0.2}
        instance.scale_controls(scale_dict)
        # Cleanup
        foot_locators_grp.visibility.set(0)

        return instance

    def remove(self):
        # Delete chains
        pm.delete(self.ctl_chain[0])
        if self.fk_control.transform.numChildren():
            self.fk_control.transform.childAtIndex(0).setParent(self.fk_control.transform.getParent())
        pm.delete(self.fk_control.group)

        # Delete attrs
        self.meta_parent.ik_control.transform.FOOT.unlock()
        pm.deleteAttr(self.meta_parent.ik_control.transform.FOOT)
        for attr_name in self.ROLL_ATTRS:
            pm.deleteAttr(self.meta_parent.ik_control.transform.attr(attr_name))
        super(FootComponent, self).remove()

    def bake_fkik(self, source="fk", time_range=None, step=1):
        if source != "ik":
            return
        Logger.info("{0}: baking foot roll to FK {1}...".format(self, time_range))

        if not time_range:
            time_range = animFn.get_playback_range()
        for frame in range(time_range[0], time_range[1] + 1, step):
            pm.setCurrentTime(frame)
            if source == "ik":
                self.fk_control.transform.attr(self.roll_axis).set(self.meta_parent.ik_control.transform.footRoll.get() * -1.0)
                self.fk_control.transform.attr(self.roll_axis).setKey()
