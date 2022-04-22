import pymel.core as pm
from luna import Logger
import luna_rig
from luna_rig.functions import jointFn
from luna_rig.functions import nameFn
from luna_rig.functions import attrFn
from luna_rig.functions import curveFn


class FKDynamicsComponent(luna_rig.AnimComponent):

    @property
    def hair_system(self):
        node = self.pynode.hairSystem.listConnections(
            d=1)[0].getShape()  # type: luna_rig.nt.HairSystem
        return node

    @property
    def offsets(self):
        nodes = self.pynode.offsets.listConnections(d=1)  # type: list
        return nodes

    @classmethod
    def create(cls,
               meta_parent,
               character=None,
               name="dynamics_component",
               unique_nsolver=False,
               tag=""):
        cls.verify_parent_type(meta_parent, luna_rig.components.FKComponent)

        # Create instance and add attrs
        instance = super(FKDynamicsComponent, cls).create(meta_parent=meta_parent, side=meta_parent.side,
                                                          name=name, character=character, tag=tag)  # type: FKDynamicsComponent
        instance.pynode.addAttr("hairSystem", at="message")
        ctl_chain = jointFn.duplicate_chain(new_joint_name=[instance.indexed_name, name],
                                            new_joint_side=instance.side,
                                            original_chain=meta_parent.ctl_chain,
                                            new_parent=instance.group_joints)

        # Create input curve:
        joint_points = [pm.xform(jnt, q=1, t=1, ws=1) for jnt in ctl_chain]
        input_curve = curveFn.curve_from_points(nameFn.generate_name([name, "input"], side=instance.side, suffix="crv"),
                                                points=joint_points,
                                                parent=instance.group_noscale)
        pm.rebuildCurve(input_curve, d=3, end=1, kep=1, rpo=1, ch=0, tol=0.01)
        meta_parent.character.root_control.transform.scale.connect(input_curve.scale)
        # Create hair system
        input_curve.select(r=1)
        pm.mel.eval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0"};')
        pm.select(cl=1)

        # Gather created nodes
        follicle = input_curve.getParent()  # type: luna_rig.nt.Transform
        hair_system = follicle.getShape().listConnections(type="hairSystem")[
            0]  # type:  luna_rig.nt.Transform
        nucleus = hair_system.getShape().listConnections(type="nucleus")[0]
        output_curve = follicle.getShape().outCurve.listConnections()[
            0]  # type: luna_rig.nt.NurbsCurve
        output_grp = output_curve.getParent()  # type:  luna_rig.nt.Transform

        # Assign nucleus
        if not unique_nsolver:
            char_nucleus = meta_parent.character.get_nucleus()
            if char_nucleus:
                pm.select(hair_system, r=1)
                pm.mel.eval("assignNSolver {0}".format(char_nucleus))
                pm.delete(nucleus)
                nucleus = char_nucleus  # type: luna_rig.nt.Nucleus
                pm.select(cl=1)
            else:
                nucleus.rename("{0}_nucl".format(meta_parent.character.name))
        else:
            old_nucleus = nucleus
            nucleus = pm.createNode("nucleus", n="{0}_nucl".format(
                instance.indexed_name))  # type: luna_rig.nt.Nucleus
            pm.select(hair_system, r=1)
            pm.mel.eval("assignNSolver {0}".format(nucleus))
            pm.select(cl=1)
            if not old_nucleus.inputActive.listConnections():
                pm.delete(old_nucleus)
        pm.parent(nucleus, meta_parent.character.root_control.transform)

        # Rename hair system objects
        hair_system.rename(nameFn.generate_name(
            [instance.name, "hair"], side=instance.side, suffix="sys"))
        follicle.rename(nameFn.generate_name([instance.name], side=instance.side, suffix="fol"))
        output_grp.rename(nameFn.generate_name(
            [instance.name, "output"], side=instance.side, suffix="grp"))
        output_curve.rename(nameFn.generate_name(
            [instance.name, "out"], side=instance.side, suffix="crv"))
        attrFn.add_meta_attr(hair_system.getShape())

        # Adjust dynamics
        follicle.getShape().pointLock.set(1)
        hair_system.getShape().bendResistance.set(0.3)

        # Parent hair objects
        hair_system.setParent(instance.group_parts)
        output_grp.setParent(instance.group_parts)

        # Create IK spline setup
        ik_handle = pm.ikHandle(n=nameFn.generate_name([instance.name], side=instance.side, suffix="ikh"),
                                sj=ctl_chain[0],
                                ee=ctl_chain[-1],
                                c=output_curve,
                                sol="ikSplineSolver",
                                roc=1,
                                pcv=0,
                                ccv=0,
                                scv=0)[0]  # type: luna_rig.nt.IkHandle
        ik_handle.setParent(instance.group_parts)

        # Store joint chains
        instance._store_ctl_chain(ctl_chain)
        hair_system.getShape().metaParent.connect(instance.pynode.hairSystem)
        # Connect to character, parent
        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent)

        # # House keeping
        if instance.character:
            instance.group_parts.visibility.set(0)
            instance.group_joints.visibility.set(0)
        return instance

    def attach_to_component(self, other_comp):
        super(FKDynamicsComponent, self).attach_to_component(other_comp, hook_index=None)
        # Add dynamics attributes
        attrFn.add_divider(self.meta_parent.controls[0].transform, attr_name="DYNAMICS")
        # TODO: Use proxy attr instead of copying
        attr_dict = attrFn.transfer_attr(
            self.hair_system, self.meta_parent.controls[0].transform, connect=True)
        for added_attr in attr_dict.values():
            self._store_settings(added_attr)
        # Create dynamics offsets
        for fk_ctl, jnt in zip(self.meta_parent.controls, self.ctl_chain):
            dynam_offset = fk_ctl.insert_offset("dynamics")
            self._store_util_nodes(dynam_offset)
            jnt.rotate.connect(dynam_offset.rotate)

    def attach_to_skeleton(self):
        pass

    def remove(self):
        # Delete attributes
        for attr in self.settings.keys():
            pm.deleteAttr(attr)
        self.meta_parent.controls[0].transform.DYNAMICS.unlock()
        pm.deleteAttr(self.meta_parent.controls[0].transform.DYNAMICS)
        super(FKDynamicsComponent, self).remove()
        self.signals.removed.emit()
