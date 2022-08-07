import pymel.core as pm

import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.rivetFn as rivetFn
import luna_rig.functions.surfaceFn as surfaceFn
from .spine_component import SpineComponent


class QuadrupedSpineComponent(SpineComponent):
    @classmethod
    def create(cls,
               start_joint,
               end_joint,
               side_vector=[1, 0, 0],
               meta_parent=None,
               character=None,
               side='c',
               name='spine',
               tag="body"):
        instance = super(QuadrupedSpineComponent, cls).create(
            meta_parent,
            character,
            side,
            name,
            tag)
        joint_chain = jointFn.joint_chain(start_joint, end_joint)
        jointFn.validate_rotations(joint_chain)
        for jnt in joint_chain:
            attrFn.add_meta_attr(jnt)

        ctl_chain = jointFn.duplicate_chain(new_joint_name=[instance.indexed_name, "ctl"],
                                            new_joint_side=instance.side,
                                            original_chain=joint_chain,
                                            new_parent=instance.group_joints)

        # Create temp curve for positioning and get joints points
        joint_points = [jnt.getTranslation(space="world") for jnt in ctl_chain]

        # Create spine surface
        # ? Loft bezier curves instead?
        nurbs_width = (joint_points[-1] - joint_points[0]).length() * 0.1  # type: float
        spine_surface = surfaceFn.loft_from_points(
            joint_points, side_vector=side_vector, width=nurbs_width)
        surfaceFn.rebuild_1_to_3(spine_surface)
        spine_surface.rename(nameFn.generate_name(instance.name, instance.side, "nurbs"))
        spine_surface.setParent(instance.group_noscale)
        # Create rivets
        rivet_joints = []
        follicles = rivetFn.FollicleRivet.along_surface(spine_surface,
                                                        side=instance.side,
                                                        name=[instance.indexed_name, "rivet"],
                                                        use_span="v",
                                                        parent=instance.group_noscale,)
        for index, jnt in enumerate(ctl_chain):
            rvt_jnt = pm.createNode("joint",
                                    n=nameFn.generate_name(
                                        [instance.indexed_name, "rivet"], instance.side, suffix="jnt"),
                                    parent=follicles[index].transform)
            pm.matchTransform(rvt_jnt, jnt, rot=1)
            pm.makeIdentity(rvt_jnt, apply=True)
            rivet_joints.append(rvt_jnt)
