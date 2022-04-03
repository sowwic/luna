import pymel.core as pm
import luna_rig
from luna import Logger
from luna_rig.functions import jointFn
from luna_rig.functions import nameFn
from luna_rig.functions import attrFn


class SimpleComponent(luna_rig.AnimComponent):

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=None,
               character=None,
               side="c",
               name="empty_component",
               tag=""):
        instance = super(SimpleComponent, cls).create(meta_parent=meta_parent, side=side, name=name, character=character, tag=tag)  # type: SimpleComponent
        instance.connect_to_character(character, parent=True)
        instance.attach_to_component(meta_parent, hook_index=hook)
        return instance

    def add_control(self, guide_object, name, as_hook=False, bind_joint=None, *args, **kwargs):
        parent = kwargs.pop("parent", None)

        new_control = luna_rig.Control.create(name=[self.indexed_name, name],
                                              guide=guide_object,
                                              parent=self.group_ctls,
                                              *args,
                                              **kwargs)
        # Connect to hook
        self._store_controls([new_control])
        if parent:
            if isinstance(parent, luna_rig.Control):
                parent = parent.transform
            pm.parentConstraint(parent, new_control.group, mo=1)
        # Store hook
        if as_hook:
            self.add_hook(new_control.transform, new_control.name)
        # Add bind joint
        if bind_joint:
            pm.parentConstraint(new_control.transform, bind_joint, mo=True)
            attrFn.add_meta_attr(bind_joint)
            self._store_bind_joints([bind_joint])
        return new_control

    def attach_to_skeleton(self):
        pass

    def attach_to_component(self, other_comp, hook_index=None):
        super(SimpleComponent, self).attach_to_component(other_comp, hook_index=hook_index)
        if self.in_hook:
            pm.parentConstraint(self.in_hook.transform, self.group_ctls)

    def add_existing_control(self, control, as_hook=False, bind_joint=None):

        control.rename(name='_'.join([self.indexed_name, control.name]))
        if not control.get_parent():
            control.set_parent(self.group_ctls)

        # Connect to hook
        self._store_controls([control])
        # Store hook
        if as_hook:
            self.add_hook(control.transform, control.name)
        # Add bind joint
        if bind_joint:
            pm.parentConstraint(control.transform, bind_joint, mo=True)
            attrFn.add_meta_attr(bind_joint)
            self._store_bind_joints([bind_joint])
