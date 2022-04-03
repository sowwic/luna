import pymel.core as pm
import luna_rig
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.nodeFn as nodeFn
from luna import Logger


class WireComponent(luna_rig.AnimComponent):

    @property
    def wire_curve(self):
        crv = self.pynode.wireCurve.get()  # type: luna_rig.nt.Transform
        return crv

    @property
    def geometry(self):
        crv = self.pynode.affectedGeometry.get()  # type: luna_rig.nt.Transform
        return crv

    @property
    def wire_deformer(self):
        dfrm = self.pynode.wireDeformer.get()  # type: luna_rig.nt.Wire
        return dfrm

    @property
    def root_control(self):
        return luna_rig.Control(self.pynode.rootControl.get())

    @property
    def shape_controls(self):
        return [luna_rig.Control(conn) for conn in self.pynode.shapeControls.listConnections(d=1)]

    @classmethod
    def create(cls,
               character=None,
               meta_parent=None,
               side='c',
               name='wire_component',
               hook=None,
               tag='',
               curve=None,
               geometry=None,
               dropoff_distance=100.0,
               num_controls=4,
               control_lines=True):
        instance = super(WireComponent, cls).create(character=character, meta_parent=meta_parent, side=side, name=name, hook=hook, tag=tag)  # type: WireComponent
        instance.pynode.addAttr("rootControl", at="message")
        instance.pynode.addAttr("shapeControls", at="message", multi=True, im=False)
        instance.pynode.addAttr("wireCurve", at="message")
        instance.pynode.addAttr("wireDeformer", at="message")
        instance.pynode.addAttr("affectedGeometry", at="message")

        if not curve or not geometry:
            Logger.error("{0}: Requires geometry and curve to build on.")
            raise ValueError
        curve = pm.PyNode(curve)  # type: luna_rig.nt.Transform
        curve.setParent(instance.group_noscale)

        # Create deformer
        wire_deformer = pm.wire(geometry, wire=curve, n=nameFn.generate_name(instance.name, instance.side, "wire"))[0]  # type: luna_rig.nt.Wire
        wire_deformer.setWireDropOffDistance(0, dropoff_distance)
        attrFn.add_meta_attr([curve, wire_deformer])

        # Create controls
        shape_controls = []
        ctl_locator = pm.spaceLocator(n="temp_control_loc")
        # Root control
        ctl_locator.translate.set(pm.pointOnCurve(curve, pr=0.0, top=1))
        root_control = luna_rig.Control.create(name=[instance.indexed_name, "root"],
                                               side=instance.side,
                                               guide=ctl_locator,
                                               parent=instance.group_ctls,
                                               delete_guide=False,
                                               attributes="trs")

        # Shape control
        for index in range(0, num_controls + 1):
            u_value = float(index) / float(num_controls)
            ctl_locator.translate.set(pm.pointOnCurve(curve, pr=u_value, top=1))
            ctl = luna_rig.Control.create(name=[instance.indexed_name, "shape"],
                                          side=instance.side,
                                          guide=ctl_locator,
                                          parent=root_control,
                                          delete_guide=False,
                                          attributes="tr",
                                          shape="joint",
                                          orient_axis="y",
                                          joint=True)
            shape_controls.append(ctl)
        pm.delete(ctl_locator)
        pm.skinCluster([each.joint for each in shape_controls], curve, n=nameFn.generate_name([instance.indexed_name, "curve"], instance.side, "skin"))

        # Draw control target lines
        if control_lines:
            for ctl in shape_controls:
                nearest_locator = pm.spaceLocator(n=nameFn.generate_name([ctl.indexed_name, "nearest"], ctl.side, suffix="loc"))
                nearest_locator.setParent(ctl.group)
                nearest_locator.inheritsTransform.set(False)
                nearest_locator.visibility.set(False)
                nearest_pt_crv = nodeFn.create("nearestPointOnCurve", [ctl.indexed_name, "wire"], ctl.side, "nrpt")
                decomp_mtx = nodeFn.create("decomposeMatrix", [ctl.indexed_name, "wire"], ctl.side, "decomp")
                ctl.joint.worldMatrix.connect(decomp_mtx.inputMatrix)
                curve.getShape().local.connect(nearest_pt_crv.inputCurve)
                decomp_mtx.outputTranslate.connect(nearest_pt_crv.inPosition)
                nearest_pt_crv.position.connect(nearest_locator.translate)
                ctl.add_wire(nearest_locator)

        # Store objects
        instance._store_controls([root_control])
        instance._store_controls(shape_controls)
        curve.metaParent.connect(instance.pynode.wireCurve)
        wire_deformer.metaParent.connect(instance.pynode.wireDeformer)
        pm.connectAttr(geometry + ".message", instance.pynode.affectedGeometry)
        root_control.transform.metaParent.connect(instance.pynode.rootControl)
        for ctl in shape_controls:
            ctl.transform.metaParent.connect(instance.pynode.shapeControls, na=True)

        # Connections
        instance.attach_to_component(meta_parent, hook_index=hook)
        instance.connect_to_character(character_component=character, parent=True)
        instance.character.root_control.transform.Scale.connect(instance.wire_deformer.scale[0])

        # Scale controls
        scale_dict = {}
        for ctl in shape_controls:
            scale_dict[ctl] = 0.02
        instance.scale_controls(scale_dict)

        # House keeping
        instance.group_parts.visibility.set(False)
        instance.group_joints.visibility.set(False)

        return instance

    # ============== Getter methods =============== #
    def get_wire_curve(self):
        return self.wire_curve

    def get_geometry(self):
        return self.geometry

    def get_wire_deformer(self):
        return self.wire_deformer

    def get_root_control(self):
        return self.root_control

    def get_shape_controls(self):
        return self.shape_controls
