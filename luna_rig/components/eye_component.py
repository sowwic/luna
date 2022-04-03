import pymel.core as pm
from luna import Logger
import luna_rig
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.transformFn as transformFn

DEFAULT_AIM_VECTOR = transformFn.WorldVector.Z.value
DEFAULT_UP_VECTOR = transformFn.WorldVector.Y.value


class EyeComponent(luna_rig.AnimComponent):

    @property
    def aim_control(self):
        return luna_rig.Control(self.pynode.aimControl.get())

    @property
    def fk_control(self):
        return luna_rig.Control(self.pynode.fkControl.get())
    # ============ Getter methods =========== #

    def get_aim_control(self):
        return self.aim_control

    def get_fk_control(self):
        return self.fk_control

    @classmethod
    def create(cls,
               aim_locator,
               eye_joint,
               side="c",
               name="eye",
               character=None,
               meta_parent=None,
               hook=0,
               aim_vector=DEFAULT_AIM_VECTOR,
               up_vector=DEFAULT_UP_VECTOR,
               target_wire=False,
               tag="face"):
        # Parse arguments
        if isinstance(aim_vector, str):
            aim_vector = aim_vector.upper()
            if aim_vector not in 'XYZ':
                Logger.warning('{0}: Aim vector must be either x, y or z. Got {1}. Using default z'.format(cls.as_str(name_only=True), aim_vector))
                aim_vector = DEFAULT_AIM_VECTOR.value
            else:
                aim_vector = transformFn.WorldVector[aim_vector].value

        if isinstance(up_vector, str):
            up_vector = up_vector.upper()
            if up_vector not in 'XYZ':
                Logger.warning('{0}: Up vector must be either x, y or z. Got {1}. Using default y'.format(cls.as_str(name_only=True), up_vector))
                up_vector = DEFAULT_UP_VECTOR.value
            else:
                up_vector = transformFn.WorldVector[up_vector].value

        # Create instance, add attributes
        instance = super(EyeComponent, cls).create(meta_parent=meta_parent, side=side, name=name, hook=hook, character=character, tag=tag)  # type: EyeComponent
        instance.pynode.addAttr("aimControl", at="message")
        instance.pynode.addAttr("fkControl", at="message")
        eye_joint = pm.PyNode(eye_joint)
        attrFn.add_meta_attr(eye_joint)

        # Controls
        fk_orient_vec = aim_vector.cross(up_vector)
        fk_control = luna_rig.Control.create(name="{0}_fk".format(instance.indexed_name),
                                             side=instance.side,
                                             guide=eye_joint,
                                             delete_guide=False,
                                             parent=instance.group_ctls,
                                             attributes="trs",
                                             joint=True,
                                             orient_axis=transformFn.get_axis_name_from_vector3(fk_orient_vec),
                                             shape="circle_pointed")

        aim_control = luna_rig.Control.create(name="{0}_aim".format(instance.indexed_name),
                                              side=instance.side,
                                              guide=aim_locator,
                                              parent=instance.group_ctls,
                                              delete_guide=True,
                                              attributes="t",
                                              shape="circle",
                                              orient_axis="z",
                                              tag="face")
        pm.aimConstraint(aim_control.transform, fk_control.group, aim=aim_vector, u=up_vector)
        if target_wire:
            aim_control.add_wire(fk_control.group)

        # Connections
        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent, hook)
        instance._store_bind_joints([eye_joint])
        instance._store_ctl_chain([fk_control.joint])
        instance._store_controls([fk_control, aim_control])
        aim_control.transform.metaParent.connect(instance.pynode.aimControl)
        fk_control.transform.metaParent.connect(instance.pynode.fkControl)

        return instance

    def attach_to_component(self, other_comp, hook_index=0):
        super(EyeComponent, self).attach_to_component(other_comp, hook_index=hook_index)
        if self.in_hook:
            pm.parentConstraint(self.in_hook.transform, self.root, mo=1)
