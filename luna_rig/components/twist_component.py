import pymel.core as pm
from luna import Logger
import luna.utils.enumFn as enumFn
import luna_rig
import luna_rig.functions.curveFn as curveFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.attrFn as attrFn


class TwistComponent(luna_rig.AnimComponent):

    class Hooks(enumFn.Enum):
        START_JNT = 0
        END_JNT = 1

    @property
    def twist_start_object(self):
        node = self.pynode.twistStartObject.listConnections(d=1)[0]  # type: luna_rig.nt.Transform
        return node

    @property
    def twist_end_object(self):
        node = self.pynode.twistEndObject.listConnections(d=1)[0]  # type: luna_rig.nt.Transform
        return node

    @property
    def start_joint(self):
        node = self.pynode.startJoint.listConnections(d=1)[0]  # type: luna_rig.nt.Joint
        return node

    @property
    def end_joint(self):
        node = self.pynode.endJoint.listConnections(d=1)[0]  # type: luna_rig.nt.Joint
        return node

    @property
    def skel_start_joint(self):
        node = self.pynode.skelStartJoint.listConnections(d=1)[0]  # type: luna_rig.nt.Joint
        return node

    @property
    def skel_end_joint(self):
        node = self.pynode.skelEndJoint.listConnections(d=1)[0]  # type: luna_rig.nt.Joint
        return node

    def get_start_hook_index(self):
        return self.Hooks.START_JNT.value

    def get_end_hook_index(self):
        return self.Hooks.END_JNT.value

    @classmethod
    def create(cls,
               meta_parent,
               character=None,
               side=None,
               name="twist",
               start_joint=None,
               end_joint=None,
               num_joints=2,
               start_object=None,
               end_object=None,
               mirrored_chain=False,
               add_hooks=False,
               tag=""):
        # Process arguments
        if not side:
            side = meta_parent.side
        # Start end joints
        if not isinstance(start_joint, pm.PyNode):
            start_joint = pm.PyNode(start_joint)

        if not end_joint:
            end_joint = start_joint.getChildren()[0]
        elif not isinstance(end_joint, pm.PyNode):
            end_joint = pm.PyNode(end_joint)

        # Start end objects
        if not start_object:
            start_object = start_joint
        if not end_object:
            end_object = end_joint
        if not isinstance(start_object, pm.PyNode):
            start_object = pm.PyNode(start_object)
        if not isinstance(end_object, pm.PyNode):
            end_object = pm.PyNode(end_object)

        name = "_".join([meta_parent.indexed_name, name])

        # Create instance and add attrs to metanode
        instance = super(TwistComponent, cls).create(meta_parent=meta_parent, side=side, name=name, hook=None, character=character, tag=tag)  # type: TwistComponent
        instance.pynode.addAttr("twistStartObject", at="message")
        instance.pynode.addAttr("twistEndObject", at="message")
        instance.pynode.addAttr("startJoint", at="message")
        instance.pynode.addAttr("endJoint", at="message")
        instance.pynode.addAttr("negativeX", at="bool", dv=mirrored_chain)
        instance.pynode.addAttr("skelStartJoint", at="message")
        instance.pynode.addAttr("skelEndJoint", at="message")

        # Skeleton connection joints
        skel_start_joint = meta_parent.bind_joints[meta_parent.ctl_chain.index(start_joint)]
        skel_end_joint = meta_parent.bind_joints[meta_parent.ctl_chain.index(end_joint)]

        # Store parameters as attrs
        start_joint.message.connect(instance.pynode.startJoint)
        end_joint.message.connect(instance.pynode.endJoint)
        start_object.message.connect(instance.pynode.twistStartObject)
        end_object.message.connect(instance.pynode.twistEndObject)
        skel_start_joint.message.connect(instance.pynode.skelStartJoint)
        skel_end_joint.message.connect(instance.pynode.skelEndJoint)

        # Create IK curve
        curve_points = [jnt.getTranslation(space="world") for jnt in [instance.start_joint, instance.end_joint]]
        ik_curve = curveFn.curve_from_points(nameFn.generate_name(instance.indexed_name, side=instance.side, suffix="crv"),
                                             degree=1,
                                             points=curve_points,
                                             parent=instance.group_noscale)
        pm.rebuildCurve(ik_curve, d=3, ch=0)
        # Create ctl chain
        ctl_chain = jointFn.along_curve(ik_curve,
                                        num_joints + 2,
                                        joint_name=instance.name,
                                        joint_side=instance.side,
                                        joint_suffix="jnt",
                                        delete_curve=False)
        attrFn.add_meta_attr(ctl_chain)
        for jnt in ctl_chain:
            pm.matchTransform(jnt, instance.start_joint, rot=1)
            pm.makeIdentity(jnt, apply=True)

        jointFn.create_chain(ctl_chain)
        ctl_chain[0].setParent(instance.group_joints)
        # Spline IK
        ik_handle = pm.ikHandle(n=nameFn.generate_name(instance.indexed_name, side=instance.side, suffix="ikh"),
                                sj=ctl_chain[0],
                                ee=ctl_chain[-1],
                                c=ik_curve,
                                sol="ikSplineSolver",
                                roc=1,
                                pcv=0,
                                ccv=0,
                                scv=0)[0]
        ik_handle.setParent(instance.group_parts)
        # Curve bind joint
        pm.select(instance.start_joint, r=1)
        crv_ik_joint = pm.joint(n=nameFn.generate_name([instance.indexed_name, "ik"], side=instance.side, suffix="jnt"))
        pm.skinCluster([crv_ik_joint], ik_curve, n=nameFn.generate_name(instance.indexed_name, side=instance.side, suffix="skin"))
        # Twist locators
        start_locator = pm.spaceLocator(n=nameFn.generate_name([instance.indexed_name, "start"], side=instance.side, suffix="loc"))
        end_locator = pm.spaceLocator(n=nameFn.generate_name([instance.indexed_name, "end"], side=instance.side, suffix="loc"))
        pm.matchTransform(start_locator, ctl_chain[0])
        pm.matchTransform(end_locator, ctl_chain[-1])
        start_locator.setParent(instance.twist_start_object)
        end_locator.setParent(instance.twist_end_object)
        # IKH advanced twist
        ik_handle.dTwistControlEnable.set(True)
        ik_handle.dWorldUpType.set(4)
        instance.pynode.negativeX.connect(ik_handle.dForwardAxis)
        start_locator.worldMatrix.connect(ik_handle.dWorldUpMatrix)
        end_locator.worldMatrix.connect(ik_handle.dWorldUpMatrixEnd)
        # Create output joints
        output_joints = jointFn.duplicate_chain(start_joint=ctl_chain[1],
                                                end_joint=ctl_chain[-2],
                                                add_name="out",
                                                new_parent=instance.group_joints)
        for ctl_jnt, out_jnt in zip(ctl_chain[1:-1], output_joints):
            pm.parentConstraint(ctl_jnt, out_jnt)

        # Add hooks
        if add_hooks:
            instance.add_hook(ctl_chain[0], "start_jnt")
            instance.add_hook(ctl_chain[-1], "end_jnt")

        # Meta connections
        instance.connect_to_character(parent=True)
        instance.attach_to_component(meta_parent, hook_index=None)
        instance._store_ctl_chain(ctl_chain)
        instance._store_bind_joints(output_joints)
        instance._store_util_nodes([start_locator, end_locator, crv_ik_joint])

        # Cleanup
        ik_curve.inheritsTransform.set(0)
        instance.group_joints.visibility.set(0)
        instance.group_parts.visibility.set(0)

        return instance

    def attach_to_skeleton(self):
        Logger.info("{0}: Attaching to skeleton...".format(self))
        if not self.twist_start_object == self.start_joint:
            constraints = self.meta_parent.bind_joints[0].listConnections(type="parentConstraint")
            if constraints:
                pm.delete(constraints)
            pm.parentConstraint(self.ctl_chain[0], self.meta_parent.bind_joints[0])
        # Insert output joints
        self.bind_joints[0].setParent(self.skel_start_joint)
