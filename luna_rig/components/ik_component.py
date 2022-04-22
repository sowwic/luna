import pymel.core as pm
from luna import Logger
from luna.utils import enumFn
import luna_rig
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.functions.curveFn as curveFn


class IKComponent(luna_rig.AnimComponent):

    class Hooks(enumFn.Enum):
        START_JNT = 0
        END_JNT = 1

    @property
    def ik_control(self):
        transform = self.pynode.ikControl.listConnections(d=1)[0]  # type: luna_rig.nt.Transform
        return luna_rig.Control(transform)

    @property
    def pv_control(self):
        transform = self.pynode.poleVectorControl.listConnections(
            d=1)  # type: luna_rig.nt.Transform
        return luna_rig.Control(transform[0]) if transform else None

    @property
    def handle(self):
        node = self.pynode.ikHandle.listConnections(d=1)[0]  # type:luna_rig.nt.IkHandle
        return node

    @property
    def group_joints_offset(self):
        transform = self.pynode.jointOffsetGrp.get()  # type: luna_rig.nt.Transform
        return transform

    # ============= Getter methods ============== #
    def get_start_hook_index(self):
        return self.Hooks.START_JNT.value

    def get_end_hook_index(self):
        return self.Hooks.END_JNT.value

    def get_ik_control(self):
        return self.ik_control

    def get_pv_control(self):
        return self.pv_control

    def get_handle(self):
        return self.handle

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=0,
               character=None,
               side="c",
               name="ik_component",
               start_joint=None,
               end_joint=None,
               control_world_orient=False,
               tag=""):
        # Create instance and add attrs
        instance = super(IKComponent, cls).create(meta_parent=meta_parent, side=side,
                                                  name=name, character=character, tag=tag)  # type: IKComponent
        instance.pynode.addAttr("ikControl", at="message")
        instance.pynode.addAttr("poleVectorControl", at="message")
        instance.pynode.addAttr("ikHandle", at="message")
        instance.pynode.addAttr("jointOffsetGrp", at="message")
        # Joint chain
        joint_chain = jointFn.joint_chain(start_joint, end_joint)
        jointFn.validate_rotations(joint_chain)

        # Create control chain
        for jnt in joint_chain:
            attrFn.add_meta_attr(jnt)
        # ctl_chain = jointFn.duplicate_chain(original_chain=joint_chain, add_name="ctl", new_parent=instance.group_joints)
        ctl_chain = jointFn.duplicate_chain(new_joint_name=[instance.indexed_name, "ctl"],
                                            new_joint_side=instance.side,
                                            original_chain=joint_chain,
                                            new_parent=instance.group_joints)

        jnt_offset_grp = nodeFn.create(
            "transform", [instance.indexed_name, "constr"], instance.side, suffix="grp", p=instance.group_joints)
        attrFn.add_meta_attr(jnt_offset_grp)
        pm.matchTransform(jnt_offset_grp, ctl_chain[0])
        ctl_chain[0].setParent(jnt_offset_grp)

        # Create ik control
        ik_control = luna_rig.Control.create(side=instance.side,
                                             name="{0}_ik".format(instance.indexed_name),
                                             guide=ctl_chain[-1],
                                             delete_guide=False,
                                             attributes="tr",
                                             parent=instance.group_ctls,
                                             shape="cube",
                                             match_orient=not control_world_orient,
                                             tag="ik")
        ik_handle = pm.ikHandle(n=nameFn.generate_name(instance.name, side=instance.side, suffix="ikh"),
                                sj=ctl_chain[0],
                                ee=ctl_chain[-1],
                                sol="ikRPsolver")[0]
        attrFn.add_meta_attr(ik_handle)
        pm.parent(ik_handle, ik_control.transform)

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
            wire_source = ctl_chain[(len(ctl_chain) - 1) / 2]
        else:
            wire_source = ctl_chain[len(ctl_chain) / 2]
        pv_control.add_wire(wire_source)

        # Store default items
        instance._store_bind_joints(joint_chain)
        instance._store_ctl_chain(ctl_chain)
        instance._store_controls([ik_control, pv_control])
        # Store component items
        ik_control.transform.metaParent.connect(instance.pynode.ikControl)
        pv_control.transform.metaParent.connect(instance.pynode.poleVectorControl)
        ik_handle.metaParent.connect(instance.pynode.ikHandle)
        jnt_offset_grp.metaParent.connect(instance.pynode.jointOffsetGrp)

        # Store attach points
        instance.add_hook(ctl_chain[0], "start_jnt")
        instance.add_hook(ctl_chain[-1], "end_jnt")
        # Connect to character, parent
        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent, hook)
        # Store settings
        # instance._store_settings()
        # Scale controls
        scale_dict = {ik_control: 0.8,
                      pv_control: 0.1}
        instance.scale_controls(scale_dict)

        # House keeping
        ik_handle.visibility.set(0)
        if instance.character:
            instance.group_parts.visibility.set(0)
            instance.group_joints.visibility.set(0)
        return instance

    def attach_to_component(self, other_comp, hook_index=0):
        super(IKComponent, self).attach_to_component(other_comp, hook_index)
        if self.in_hook:
            pm.parentConstraint(self.in_hook.transform, self.group_joints_offset, mo=1)

    def attach_to_skeleton(self):
        """Override: attach to skeleton"""
        for ctl_jnt, bind_jnt in zip(self.ctl_chain[:-1], self.bind_joints[:-1]):
            pm.parentConstraint(ctl_jnt, bind_jnt, mo=1)


class IKSplineComponent(luna_rig.AnimComponent):

    @property
    def ik_curve(self):
        crv = self.pynode.ikCurve.get()  # type: luna_rig.nt.Transform
        return crv

    @property
    def root_control(self):
        return luna_rig.Control(self.pynode.rootControl.get())

    @property
    def shape_controls(self):
        return [luna_rig.Control(conn) for conn in self.pynode.shapeControls.listConnections(d=1)]

    # ============= Getter methods ============== #
    def get_ik_curve(self):
        return self.ik_curve

    def get_root_control(self):
        return self.root_control

    def get_shape_controls(self):
        return self.shape_controls

    @classmethod
    def create(cls,
               meta_parent=None,
               side='c',
               name='anim_component',
               hook=None,
               character=None,
               tag='',
               start_joint=None,
               end_joint=None,
               ik_curve=None,
               num_controls=None,
               control_lines=True):
        # Parse arguments
        num_controls = int(num_controls) if not isinstance(num_controls, int) else num_controls

        # Create instance and add attributes
        instance = super(IKSplineComponent, cls).create(meta_parent=meta_parent, side=side,
                                                        name=name, hook=hook, character=character, tag=tag)  # type: IKSplineComponent
        instance.pynode.addAttr("ikCurve", at="message")
        instance.pynode.addAttr("rootControl", at="message")
        instance.pynode.addAttr("shapeControls", at="message", multi=True, im=False)

        if not start_joint and not ik_curve:
            Logger.error(
                "{0}: Requires start joint or curve to build on. Got neither".format(instance))
            raise ValueError

        # Create joint chain if not provided
        if not start_joint:
            pass
        else:
            joint_chain = jointFn.joint_chain(start_joint=start_joint, end_joint=end_joint)
        attrFn.add_meta_attr(joint_chain)
        ctl_chain = jointFn.duplicate_chain(new_joint_name=[instance.indexed_name, "ctl"],
                                            new_joint_side=instance.side,
                                            original_chain=joint_chain,
                                            new_parent=instance.group_joints)

        # Build curve if not provided
        if not ik_curve:
            ik_curve_points = [jnt.getTranslation(space="world") for jnt in joint_chain]
            ik_curve = curveFn.curve_from_points(name=nameFn.generate_name([instance.indexed_name, "ik"], side=instance.side, suffix="crv"),
                                                 points=ik_curve_points,
                                                 parent=instance.group_noscale)
            pm.rebuildCurve(ik_curve, d=3, kep=1, rpo=1, ch=0, tol=0.01, spans=4)
        attrFn.add_meta_attr(ik_curve)

        # IK handle
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

        # Create controls
        if not num_controls:
            num_controls = len(ctl_chain)
        shape_controls = []

        ctl_locator = pm.spaceLocator(n="temp_control_loc")
        # Root control
        ctl_locator.translate.set(pm.pointOnCurve(ik_curve, pr=0.0, top=1))
        root_control = luna_rig.Control.create(name=[instance.indexed_name, "root"],
                                               side=instance.side,
                                               guide=ctl_locator,
                                               parent=instance.group_ctls,
                                               delete_guide=False,
                                               attributes="trs")

        # Shape control
        for index in range(0, num_controls + 1):
            u_value = float(index) / float(num_controls)
            ctl_locator.translate.set(pm.pointOnCurve(ik_curve, pr=u_value, top=1))
            ctl = luna_rig.Control.create(name=[instance.indexed_name, "shape"],
                                          side=instance.side,
                                          guide=ctl_locator,
                                          parent=root_control,
                                          delete_guide=False,
                                          attributes="tr",
                                          shape="circle",
                                          orient_axis="y",
                                          joint=True)
            shape_controls.append(ctl)
        pm.delete(ctl_locator)
        pm.skinCluster([each.joint for each in shape_controls], ik_curve, n=nameFn.generate_name(
            [instance.indexed_name, "curve"], instance.side, "skin"))

        if control_lines:
            for ctl in shape_controls:
                if ctl is shape_controls[-1]:
                    ctl.add_wire(ctl_chain[-1])
                else:
                    nearest_locator = pm.spaceLocator(n=nameFn.generate_name(
                        [ctl.indexed_name, "nearest"], ctl.side, suffix="loc"))
                    nearest_locator.setParent(ctl.group)
                    nearest_locator.inheritsTransform.set(False)
                    nearest_locator.visibility.set(False)
                    nearest_pt_crv = nodeFn.create("nearestPointOnCurve", [
                                                   ctl.indexed_name, "wire"], ctl.side, "nrpt")
                    decomp_mtx = nodeFn.create(
                        "decomposeMatrix", [ctl.indexed_name, "wire"], ctl.side, "decomp")
                    ctl.joint.worldMatrix.connect(decomp_mtx.inputMatrix)
                    ik_curve.getShape().local.connect(nearest_pt_crv.inputCurve)
                    decomp_mtx.outputTranslate.connect(nearest_pt_crv.inPosition)
                    nearest_pt_crv.position.connect(nearest_locator.translate)
                    ctl.add_wire(nearest_locator)

        # Store objects
        instance._store_bind_joints(joint_chain)
        instance._store_ctl_chain(ctl_chain)
        instance._store_controls(shape_controls)
        instance._store_controls([root_control])
        ik_curve.metaParent.connect(instance.pynode.ikCurve)
        root_control.transform.metaParent.connect(instance.pynode.rootControl)
        for ctl in shape_controls:
            ctl.transform.metaParent.connect(instance.pynode.shapeControls, na=True)

        # Connections
        instance.attach_to_component(meta_parent, hook_index=hook)
        instance.connect_to_character(character_component=character, parent=True)

        # Scale controls
        scale_dict = {}
        for ctl in shape_controls:
            scale_dict[ctl] = 0.06
        instance.scale_controls(scale_dict)

        # House keeping
        instance.group_parts.visibility.set(False)
        instance.group_joints.visibility.set(False)

        return instance

    def attach_to_component(self, other_comp, hook_index=None):
        super(IKSplineComponent, self).attach_to_component(other_comp, hook_index=hook_index)
        if self.in_hook:
            pm.parentConstraint(self.in_hook.transform, self.root_control.group, mo=1)
