import pymel.core as pm

from luna import Logger
from luna.utils import enumFn
import luna_rig
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.curveFn as curveFn
import luna_rig.functions.surfaceFn as surfaceFn
import luna_rig.functions.rivetFn as rivetFn
import luna_rig.functions.nodeFn as nodeFn


class SpineComponent(luna_rig.AnimComponent):

    @property
    def root_control(self):
        return luna_rig.Control(self.pynode.rootControl.listConnections()[0])

    @property
    def hips_control(self):
        return luna_rig.Control(self.pynode.hipsControl.listConnections()[0])

    @property
    def chest_control(self):
        return luna_rig.Control(self.pynode.chestControl.listConnections()[0])

    # ========= Getter methods ========== #
    def get_root_control(self):
        return self.root_control

    def get_hips_control(self):
        return self.hips_control

    def get_chest_control(self):
        return self.chest_control

    @classmethod
    def create(cls,
               meta_parent=None,
               character=None,
               side='c',
               name='spine',
               tag="body"):
        # Create instance and add attrs
        instance = super(SpineComponent, cls).create(meta_parent=meta_parent, side=side,
                                                     name=name, character=character, tag=tag)  # type: SpineComponent
        instance.pynode.addAttr("rootControl", at="message")
        instance.pynode.addAttr("hipsControl", at="message")
        instance.pynode.addAttr("chestControl", at="message")
        return instance


class FKIKSpineComponent(SpineComponent):

    class Hooks(enumFn.Enum):
        ROOT = 0
        HIPS = 1
        MID = 2
        CHEST = 3

    @property
    def mid_control(self):
        return luna_rig.Control(self.pynode.midControl.listConnections()[0])

    @property
    def fk1_control(self):
        return luna_rig.Control(self.pynode.fkControls.listConnections()[0])

    @property
    def fk2_control(self):
        return luna_rig.Control(self.pynode.fkControls.listConnections()[1])

    @property
    def pivot_control(self):
        if not self.pynode.hasAttr("pivotControl"):
            return None
        else:
            return luna_rig.Control(self.pynode.pivotControl.listConnections()[0])

    @property
    def ik_curve(self):
        crv = self.pynode.ikCurve.get()  # type: luna_rig.nt.Transform
        return crv

    # ========= Getter methods ========== #
    def get_mid_control(self):
        return self.mid_control

    def get_fk1_control(self):
        return self.fk1_control

    def get_fk2_control(self):
        return self.fk2_control

    def get_pivot_control(self):
        return self.pivot_control

    def get_ik_curve(self):
        return self.ik_curve

    def get_root_hook_index(self):
        return self.Hooks.ROOT.value

    def get_hips_hook_index(self):
        return self.Hooks.HIPS.value

    def get_mid_hook_index(self):
        return self.Hooks.MID.value

    def get_chest_hook_index(self):
        return self.Hooks.CHEST.value

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=0,
               character=None,
               side='c',
               name='spine',
               start_joint=None,
               end_joint=None,
               tag="body"):
        # Create instance and add attrs
        instance = super(FKIKSpineComponent, cls).create(meta_parent=meta_parent, side=side,
                                                         name=name, character=character, tag=tag)  # type: FKIKSpineComponent
        instance.pynode.addAttr("fkControls", at="message", multi=1, im=0)
        instance.pynode.addAttr("midControl", at="message")
        instance.pynode.addAttr("ikCurve", at="message")

        # Joint chains
        joint_chain = jointFn.joint_chain(start_joint, end_joint)
        jointFn.validate_rotations(joint_chain)
        for jnt in joint_chain:
            attrFn.add_meta_attr(jnt)
        # ctl_chain = jointFn.duplicate_chain(original_chain=joint_chain, add_name="ctl", new_parent=instance.group_joints)
        ctl_chain = jointFn.duplicate_chain(new_joint_name=[instance.indexed_name, "ctl"],
                                            new_joint_side=instance.side,
                                            original_chain=joint_chain,
                                            new_parent=instance.group_joints)

        # Create IK curve and handle
        ik_curve_points = [jnt.getTranslation(space="world") for jnt in joint_chain]
        ik_curve = curveFn.curve_from_points(name=nameFn.generate_name([instance.indexed_name, "ik"], side=instance.side, suffix="crv"),
                                             points=ik_curve_points,
                                             parent=instance.group_noscale)
        attrFn.add_meta_attr(ik_curve)
        pm.rebuildCurve(ik_curve, d=3, kep=1, rpo=1, ch=0, tol=0.01, spans=4)
        ik_handle = pm.ikHandle(n=nameFn.generate_name([instance.name], side=instance.side, suffix="ikh"),
                                sj=ctl_chain[0],
                                ee=ctl_chain[-1],
                                c=ik_curve,
                                sol="ikSplineSolver",
                                roc=1,
                                pcv=0,
                                ccv=0,
                                scv=0)[0]
        pm.parent(ik_handle, instance.group_parts)

        # Create IK controls
        ctl_locator = pm.spaceLocator(n="temp_control_loc")
        ctl_locator.translate.set(pm.pointOnCurve(ik_curve, pr=0.0, top=1))
        # Root
        root_control = luna_rig.Control.create(side=instance.side,
                                               name="{0}_root".format(instance.indexed_name),
                                               guide=ctl_locator,
                                               delete_guide=False,
                                               parent=instance.group_ctls,
                                               joint=False,
                                               attributes="tr",
                                               color="red",
                                               shape="root",
                                               orient_axis="y")
        # Hips
        hips_control = luna_rig.Control.create(side=instance.side,
                                               name="{0}_hips".format(instance.indexed_name),
                                               guide=ctl_locator,
                                               delete_guide=False,
                                               parent=root_control,
                                               joint=True,
                                               attributes="tr",
                                               shape="hips",
                                               orient_axis="y")
        # Mid
        ctl_locator.translate.set(pm.pointOnCurve(ik_curve, pr=0.5, top=1))
        mid_control = luna_rig.Control.create(side=instance.side,
                                              name="{0}_mid".format(instance.indexed_name),
                                              guide=ctl_locator,
                                              delete_guide=False,
                                              parent=root_control,
                                              joint=True,
                                              attributes="tr",
                                              shape="circle",
                                              orient_axis="y")
        mid_control.transform.addAttr("followChest", at="float", dv=0.0, k=1)
        mid_control.transform.addAttr("followHips", at="float", dv=0.0, k=1)
        # Chest
        ctl_locator.translate.set(pm.pointOnCurve(ik_curve, pr=1.0, top=1))
        chest_control = luna_rig.Control.create(side=instance.side,
                                                name="{0}_chest".format(instance.indexed_name),
                                                guide=ctl_locator,
                                                delete_guide=False,
                                                parent=root_control,
                                                joint=True,
                                                attributes="tr",
                                                shape="chest",
                                                orient_axis="y")
        # Connect IK controls
        # type: luna_rig.nt.ParentConstraint
        mid_ctl_constr = pm.parentConstraint(
            hips_control.transform, chest_control.transform, mid_control.group, mo=1)
        mid_control.transform.followHips.connect(mid_ctl_constr.getWeightAliasList()[0])
        mid_control.transform.followChest.connect(mid_ctl_constr.getWeightAliasList()[1])
        # Skin to curve
        pm.skinCluster([hips_control.joint, mid_control.joint, chest_control.joint],
                       ik_curve,
                       n=nameFn.generate_name(instance.name, instance.side, suffix="skin"))

        # Add twist
        ik_handle.dTwistControlEnable.set(1)
        ik_handle.dWorldUpType.set(4)
        hips_control.transform.worldMatrix.connect(ik_handle.dWorldUpMatrix)
        chest_control.transform.worldMatrix.connect(ik_handle.dWorldUpMatrixEnd)
        ik_handle.dWorldUpVectorZ.set(1)
        ik_handle.dWorldUpVectorY.set(0)
        ik_handle.dWorldUpVectorEndZ.set(1)
        ik_handle.dWorldUpVectorEndY.set(0)

        # Create FK controls
        ctl_locator.translate.set(pm.pointOnCurve(ik_curve, pr=0.25, top=1))
        fk1_control = luna_rig.Control.create(side=instance.side,
                                              name="{0}_fk".format(instance.indexed_name),
                                              guide=ctl_locator,
                                              delete_guide=False,
                                              parent=root_control,
                                              joint=True,
                                              attributes="tr",
                                              shape="circleCrossed",
                                              orient_axis="y")
        ctl_locator.translate.set(pm.pointOnCurve(ik_curve, pr=0.75, top=1))
        fk2_control = luna_rig.Control.create(side=instance.side,
                                              name="{0}_fk".format(instance.indexed_name),
                                              guide=ctl_locator,
                                              delete_guide=True,
                                              parent=fk1_control,
                                              joint=True,
                                              attributes="tr",
                                              shape="circleCrossed",
                                              orient_axis="y")
        pm.matchTransform(fk2_control.joint, ctl_chain[-1])
        pm.makeIdentity(fk2_control.joint, apply=True)
        pm.parentConstraint(fk2_control.joint, chest_control.group, mo=1)

        # Store default items
        instance._store_bind_joints(joint_chain)
        instance._store_ctl_chain(ctl_chain)
        instance._store_controls([root_control, hips_control, mid_control,
                                 chest_control, fk1_control, fk2_control])

        # Store indiviual items
        fk1_control.transform.metaParent.connect(instance.pynode.fkControls, na=1)
        fk2_control.transform.metaParent.connect(instance.pynode.fkControls, na=1)
        root_control.transform.metaParent.connect(instance.pynode.rootControl)
        hips_control.transform.metaParent.connect(instance.pynode.hipsControl)
        mid_control.transform.metaParent.connect(instance.pynode.midControl)
        chest_control.transform.metaParent.connect(instance.pynode.chestControl)
        ik_curve.metaParent.connect(instance.pynode.ikCurve)

        # Store attach points
        instance.add_hook(root_control.transform, "root")
        instance.add_hook(ctl_chain[0], "hips")
        instance.add_hook(mid_control.transform, "mid")
        instance.add_hook(ctl_chain[-1], "chest")

        # Connect to character, metaparent
        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent, hook)

        # Store settings
        instance._store_settings(mid_control.transform.followChest)
        instance._store_settings(mid_control.transform.followHips)

        # Scale controls
        scale_dict = {root_control: 0.25,
                      hips_control: 0.25,
                      mid_control: 1.2,
                      chest_control: 0.25,
                      fk1_control: 0.4,
                      fk2_control: 0.4}
        instance.scale_controls(scale_dict)

        # House keeping
        ik_handle.visibility.set(0)
        instance.group_parts.visibility.set(0)
        instance.group_joints.visibility.set(0)

        return instance


class RibbonSpineComponent(SpineComponent):
    class Hooks(enumFn.Enum):
        ROOT = 0
        HIPS = 1
        MID = 2
        CHEST = 3

    @property
    def mid_control(self):
        return luna_rig.Control(self.pynode.midControl.listConnections()[0])

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=0,
               character=None,
               side='c',
               name='spine',
               start_joint=None,
               end_joint=None,
               side_vector=[1, 0, 0],
               tag="body"):
        Logger.warning("{0}: WIP component".format(cls))
        # Create instance and add attrs
        instance = super(RibbonSpineComponent, cls).create(meta_parent=meta_parent, side=side,
                                                           name=name, character=character, tag=tag)  # type: RibbonSpineComponent
        instance.pynode.addAttr("midControl", at="message")

        # Joint chains
        joint_chain = jointFn.joint_chain(start_joint, end_joint)
        jointFn.validate_rotations(joint_chain)
        for jnt in joint_chain:
            attrFn.add_meta_attr(jnt)
            ctl_chain = jointFn.duplicate_chain(new_joint_name=[instance.indexed_name, "ctl"],
                                                new_joint_side=instance.side,
                                                original_chain=joint_chain,
                                                new_parent=instance.group_joints)

            ctl_spine_chain = ctl_chain[1:]
            ctl_pelvis_joint = ctl_chain[0]

            # Create temp curve for positioning and get joints points
            joint_points = [jnt.getTranslation(space="world") for jnt in ctl_chain]

            # Create spiene surface
            # ? Loft besize curves instead?
            nurbs_width = (joint_points[-1] - joint_points[0]).length() * 0.1
            spine_surface = surfaceFn.loft_from_points(
                joint_points[1:], side_vector=side_vector, width=nurbs_width)
            surfaceFn.rebuild_1_to_3(spine_surface)
            spine_surface.rename(nameFn.generate_name(instance.name, instance.side, "nurbs"))
            spine_surface.setParent(instance.group_noscale)
            # Create rivets
            rivet_joints = []
            follicles = rivetFn.FollicleRivet.along_surface(spine_surface,
                                                            side=instance.side,
                                                            name=[instance.indexed_name, "rivet"],
                                                            use_span="v",
                                                            parent=instance.group_noscale)
            for index, jnt in enumerate(ctl_spine_chain):
                rvt_jnt = pm.createNode("joint",
                                        n=nameFn.generate_name(
                                            [instance.indexed_name, "rivet"], instance.side, suffix="jnt"),
                                        parent=follicles[index].transform)
                pm.matchTransform(rvt_jnt, jnt, rot=1)
                pm.makeIdentity(rvt_jnt, apply=True)
                rivet_joints.append(rvt_jnt)

            # Create controls
            temp_curve = curveFn.curve_from_points(
                name="temp_spine_curve", degree=1, points=joint_points)
            pm.rebuildCurve(temp_curve, d=3, rpo=1, ch=0)
            ctl_locator = pm.spaceLocator(n="temp_control_loc")
            ctl_locator.translate.set(pm.pointOnCurve(temp_curve, pr=0.0, top=1))
            # Root
            root_control = luna_rig.Control.create(side=instance.side,
                                                   name="{0}_root".format(instance.indexed_name),
                                                   guide=ctl_locator,
                                                   delete_guide=False,
                                                   parent=instance.group_ctls,
                                                   joint=False,
                                                   attributes="tr",
                                                   color="red",
                                                   shape="root",
                                                   orient_axis="y")
            # Hips
            hips_control = luna_rig.Control.create(side=instance.side,
                                                   name="{0}_hips".format(instance.indexed_name),
                                                   guide=ctl_locator,
                                                   delete_guide=False,
                                                   parent=root_control,
                                                   joint=True,
                                                   attributes="tr",
                                                   shape="hips",
                                                   orient_axis="y")
            hips_control.transform.rotateOrder.set(1)
            # Mid
            ctl_locator.translate.set(pm.pointOnCurve(temp_curve, pr=0.5, top=1))
            mid_control = luna_rig.Control.create(side=instance.side,
                                                  name="{0}_mid".format(instance.indexed_name),
                                                  guide=ctl_locator,
                                                  delete_guide=False,
                                                  parent=root_control,
                                                  joint=True,
                                                  attributes="tr",
                                                  shape="circle",
                                                  orient_axis="y")
            # Chest
            ctl_locator.translate.set(pm.pointOnCurve(temp_curve, pr=1.0, top=1))
            chest_control = luna_rig.Control.create(side=instance.side,
                                                    name="{0}_chest".format(instance.indexed_name),
                                                    guide=ctl_locator,
                                                    delete_guide=True,
                                                    parent=root_control,
                                                    joint=True,
                                                    attributes="tr",
                                                    shape="chest",
                                                    orient_axis="y")
            chest_control.transform.rotateOrder.set(1)
            pm.delete(temp_curve)
            # Connect rivet joints to control chain
            for ctl_jnt, rvt_jnt in zip(ctl_spine_chain[:-1], rivet_joints):
                pm.pointConstraint(rvt_jnt, ctl_jnt)
                pm.orientConstraint(rvt_jnt, ctl_jnt)
            # Connect chest joint to control
            pm.matchTransform(chest_control.joint, ctl_chain[-1])
            pm.makeIdentity(chest_control.joint, apply=True)
            pm.pointConstraint(chest_control.joint, ctl_spine_chain[-1])
            pm.orientConstraint(chest_control.joint, ctl_spine_chain[-1])
            # Connect pelvis joint to control
            pm.matchTransform(hips_control.joint, ctl_pelvis_joint)
            pm.makeIdentity(chest_control.joint, apply=True)
            pm.pointConstraint(hips_control.joint, ctl_pelvis_joint)
            pm.orientConstraint(hips_control.joint, ctl_pelvis_joint)
            # Connect controls to spine surface
            pm.skinCluster(hips_control.joint, mid_control.joint,
                           chest_control.joint, spine_surface)

            # Add mid bending
            # Hips driver
            hip_driver_base_joint = pm.createNode("joint", n=nameFn.generate_name(
                [instance.indexed_name, "driver", "base"], instance.side, "jnt"))
            pm.matchTransform(hip_driver_base_joint, hips_control.transform)
            hip_driver_end_joint = pm.createNode("joint",
                                                 n=nameFn.generate_name([instance.indexed_name, "driver", "base", "end"], instance.side, "jnt"))
            pm.matchTransform(hip_driver_end_joint, mid_control.transform)
            hip_driver_end_joint.setParent(hip_driver_base_joint)
            hip_driver_base_joint.setParent(hips_control.transform)
            lower_bend_locator = pm.spaceLocator(n=nameFn.generate_name(
                [instance.indexed_name, "lower", "bend"], instance.side, "loc"))
            pm.matchTransform(lower_bend_locator, hip_driver_end_joint)
            lower_bend_locator.setParent(hips_control.group)
            pm.pointConstraint(hip_driver_end_joint, lower_bend_locator)
            # Chest driver
            chest_driver_base_joint = pm.createNode("joint", n=nameFn.generate_name(
                [instance.indexed_name, "driver", "top"], instance.side, "jnt"))
            pm.matchTransform(chest_driver_base_joint, chest_control.transform)
            chest_driver_end_joint = pm.createNode("joint",
                                                   n=nameFn.generate_name([instance.indexed_name, "driver", "top", "end"], instance.side, "jnt"))
            pm.matchTransform(chest_driver_end_joint, mid_control.transform)
            chest_driver_end_joint.setParent(chest_driver_base_joint)
            chest_driver_base_joint.setParent(chest_control.transform)
            upper_bend_locator = pm.spaceLocator(n=nameFn.generate_name(
                [instance.indexed_name, "upper", "bend"], instance.side, "loc"))
            pm.matchTransform(upper_bend_locator, chest_driver_end_joint)
            upper_bend_locator.setParent(chest_control.group)
            pm.pointConstraint(chest_driver_end_joint, upper_bend_locator)
            # Connect bend
            mid_bend_offset = mid_control.insert_offset("bend")
            # Side
            mid_bend_side_pma = nodeFn.create(
                "plusMinusAverage", [instance.indexed_name, "bend", "side"], instance.side, suffix="pma")
            upper_bend_locator.translateX.connect(mid_bend_side_pma.input1D[0])
            lower_bend_locator.translateX.connect(mid_bend_side_pma.input1D[1])
            mid_bend_side_pma.output1D.connect(mid_bend_offset.translateX)
            # Front
            mid_bend_front_pma = nodeFn.create(
                "plusMinusAverage", [instance.indexed_name, "bend", "front"], instance.side, suffix="pma")
            upper_bend_locator.translateZ.connect(mid_bend_front_pma.input1D[0])
            lower_bend_locator.translateZ.connect(mid_bend_front_pma.input1D[1])
            mid_bend_front_pma.output1D.connect(mid_bend_offset.translateZ)

            # Store default items
            instance._store_bind_joints(joint_chain)
            instance._store_ctl_chain(ctl_chain)
            instance._store_controls([root_control, hips_control, mid_control, chest_control])

            # Store indiviual items
            root_control.transform.metaParent.connect(instance.pynode.rootControl)
            hips_control.transform.metaParent.connect(instance.pynode.hipsControl)
            mid_control.transform.metaParent.connect(instance.pynode.midControl)
            chest_control.transform.metaParent.connect(instance.pynode.chestControl)

            # Store attach points
            instance.add_hook(root_control.transform, "root")
            instance.add_hook(ctl_chain[0], "hips")
            instance.add_hook(mid_control.transform, "mid")
            instance.add_hook(ctl_chain[-1], "chest")

            # Connect to character, metaparent
            instance.connect_to_character(parent=True)
            instance.attach_to_component(meta_parent, hook)

            # Store settings

            # Scale controls
            scale_dict = {root_control: 0.25,
                          hips_control: 0.25,
                          mid_control: 1.2,
                          chest_control: 0.25}
            instance.scale_controls(scale_dict)

            # House keeping
            hip_driver_base_joint.visibility.set(0)
            chest_driver_base_joint.visibility.set(0)
            lower_bend_locator.visibility.set(0)
            upper_bend_locator.visibility.set(0)
            instance.group_parts.visibility.set(0)
            instance.group_joints.visibility.set(0)

            return instance
