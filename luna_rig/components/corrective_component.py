# Based on https://vimeo.com/295232753 by Mateusz Matejczyk

import pymel.core as pm
from luna import Logger
import luna_rig
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.nodeFn as nodeFn


class CorrectiveComponent(luna_rig.AnimComponent):
    @classmethod
    def create(cls,
               meta_parent=None,
               character=None,
               side='c',
               name='corrective_component',
               tag="corrective"):
        instance = super(CorrectiveComponent, cls).create(meta_parent=meta_parent, side=side, name=name, hook=None, character=character, tag=tag)  # type: CorrectiveComponent
        instance.connect_to_character(character_component=character, parent=True)

        return instance

    def add_control(self, constr_parent, output_jnt, name="helper"):
        corr_control = luna_rig.Control.create(name=[self.indexed_name, name],
                                               side=self.side,
                                               guide=output_jnt,
                                               delete_guide=False,
                                               attributes="trs",
                                               parent=self.group_ctls,
                                               offset_grp=False,
                                               joint=True,
                                               tag="corrective")
        corr_control.insert_offset(extra_name="sdk")
        pm.parentConstraint(constr_parent, corr_control.group, mo=True)

        self._store_ctl_chain([corr_control.joint])
        self._store_bind_joints([output_jnt])
        self._store_controls([corr_control])
        return corr_control

    def get_pose_dict(self):
        pose_dict = {}
        for index, corr_control in enumerate(self.controls):
            sdk_offset = corr_control.find_offset("sdk")
            pose_translate = corr_control.transform.translate.get() + sdk_offset.translate.get()
            pose_rotate = corr_control.transform.rotate.get() + sdk_offset.rotate.get()
            pose_scale = corr_control.transform.scale.get()

            pose_dict[corr_control.transform.name()] = {}
            pose_dict[corr_control.transform.name()]["translate"] = list(pose_translate)
            pose_dict[corr_control.transform.name()]["rotate"] = list(pose_rotate)
            pose_dict[corr_control.transform.name()]["scale"] = list(pose_scale)

        return pose_dict

    def attach_to_skeleton(self):
        super(CorrectiveComponent, self).attach_to_skeleton()
        for ctl_jnt, bind_jnt in zip(self.ctl_chain, self.bind_joints):
            pm.scaleConstraint(ctl_jnt, bind_jnt)
