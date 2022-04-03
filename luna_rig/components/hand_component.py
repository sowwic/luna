import pymel.core as pm
import luna_rig
from luna_rig.importexport.driven_pose import DrivenPoseManager


class HandComponent(luna_rig.AnimComponent):

    @property
    def fingers(self):
        connections = self.pynode.fingers.listConnections()  # type: list
        finger_comps = [luna_rig.MetaNode(node) for node in connections]
        return finger_comps

    @property
    def controls(self):
        finger_controls = []
        for finger in self.fingers:
            finger_controls += finger.controls
        return finger_controls

    @classmethod
    def create(cls,
               meta_parent=None,
               character=None,
               side=None,
               name="hand",
               hook=None,
               tag="body"):
        instance = super(HandComponent, cls).create(meta_parent=meta_parent, side=side, name=name, hook=hook, character=character, tag=tag)  # type: HandComponent
        instance.pynode.addAttr("fingers", at="message", multi=True, im=False)

        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent, hook)

        return instance

    def add_fk_finger(self, start_joint, end_joint=None, name="finger", end_control=False):
        if "finger" not in name:
            name = name + "_finger"
        fk_component = luna_rig.components.FKComponent.create(meta_parent=self,
                                                              hook=None,
                                                              side=self.side,
                                                              name=name,
                                                              start_joint=start_joint,
                                                              end_joint=end_joint,
                                                              add_end_ctl=end_control,
                                                              lock_translate=False)
        fk_component.root.setParent(self.group_ctls)
        fk_component.pynode.metaParent.connect(self.pynode.fingers, na=1)
        # Adjust shapes
        fk_component.controls[0].shape = "markerDiamond"
        fk_component.controls[0].scale(1.0, 0.5)
        for ctl in fk_component.controls[1:]:
            ctl.shape = "cube"
            ctl.scale(1.0, 2)
        return fk_component

    def five_finger_setup(self, thumb_start, index_start, middle_start, ring_start, pinky_start, tip_control=False):
        names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        out_fingers = []
        for name, joint_name in zip(names, (thumb_start, index_start, middle_start, ring_start, pinky_start)):
            out_fingers.append(self.add_fk_finger(joint_name, end_control=None, name='{0}_finger'.format(name), end_joint=tip_control))
        return out_fingers

    def attach_to_component(self, other_comp, hook_index=None):
        super(HandComponent, self).attach_to_component(other_comp, hook_index=hook_index)
        if self.in_hook:
            pm.matchTransform(self.root, self.in_hook.transform)
            pm.parentConstraint(self.in_hook.transform, self.group_ctls)
