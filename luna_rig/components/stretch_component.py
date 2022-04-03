from luna import Logger
import luna_rig
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.functions.attrFn as attrFn


class IKSplineStretchComponent(luna_rig.Component):

    @property
    def ik_curve(self):
        try:
            curve_transform = self.meta_parent.pynode.ikCurve.get()  # type: luna_rig.nt.Transform
        except AttributeError:
            Logger.exception("{0}: Parent component with IKCurve attribute not found. No override curve provided.")
            raise
        return curve_transform

    @classmethod
    def create(cls,
               meta_parent,
               side=None,
               name='stretch',
               switch_control=None,
               default_state=False,
               switch_attr="stretch",
               stretch_axis="x",
               tag="stretch",):
        if not isinstance(meta_parent, luna_rig.AnimComponent):
            Logger.error("{0}: Must have AnimComponent instance as meta_parent".format(cls))
            raise TypeError

        if switch_control and not isinstance(switch_control, luna_rig.Control):
            switch_control = luna_rig.Control(switch_control)

        if not side:
            side = meta_parent.side

        # Full name based on parent component
        full_name = "_".join([meta_parent.indexed_name, name])
        instance = super(IKSplineStretchComponent, cls).create(meta_parent, side=side, name=full_name, tag=tag)  # type: IKSplineStretchComponent

        # Apply stretch
        curve_info = nodeFn.create("curveInfo", [instance.name, "curve"], instance.side, suffix="info")
        instance.ik_curve.getShape().worldSpace.connect(curve_info.inputCurve)
        # Divide initial length by current
        final_scale_mdv = nodeFn.create("multiplyDivide", [instance.name, "pure"], instance.side, suffix="mdv")
        final_scale_mdv.operation.set(2)
        curve_info.arcLength.connect(final_scale_mdv.input1X)

        # Counter scale
        counter_scale_mdv = nodeFn.create("multiplyDivide", [instance.name, "scaled"], instance.side, suffix="mdv")
        meta_parent.character.root_control.transform.Scale.connect(counter_scale_mdv.input1X)
        counter_scale_mdv.input2X.set(curve_info.arcLength.get())
        counter_scale_mdv.outputX.connect(final_scale_mdv.input2X)

        if switch_control:
            switch_control.transform.addAttr(switch_attr, at="bool", k=1, dv=default_state)
            switch_choice = nodeFn.create("choice", [instance.name, "switch"], instance.side, suffix="mdl")
            switch_control.transform.attr(switch_attr).connect(switch_choice.selector)
            switch_choice.input[0].set(1.0)
            final_scale_mdv.outputX.connect(switch_choice.input[1])
            for jnt in meta_parent.ctl_chain:
                switch_choice.output.connect(jnt.attr("s{0}".format(stretch_axis)))
        else:
            Logger.warning("{0}: No control was used for state control")


class IKStretchComponent(luna_rig.Component):

    @property
    def state(self):
        value = self.pynode.state.get()  # type: bool
        return value

    @state.setter
    def state(self, value):
        plug = self.pynode.state.listConnections(d=1, plugs=1)[0]
        plug.set(value)

    @property
    def threshold(self):
        value = self.pynode.threshold.get()  # type: float
        return value

    @threshold.setter
    def threshold(self, value):
        plug = self.pynode.threshold.listConnections(d=1, plugs=1)[0]
        plug.set(value)

    @classmethod
    def create(cls,
               meta_parent,
               side=None,
               name="stretch",
               tag="stretch",
               default_state=False,
               stretch_axis="x",
               threshold=0.0,
               toggle_attr_name="stretch",
               threshold_attr_name="stretchThreshold"):
        cls.verify_parent_type(meta_parent, (luna_rig.components.IKComponent, luna_rig.components.FKIKComponent))
        side = side if side else meta_parent.side
        name = [meta_parent.indexed_name, name]
        instance = super(IKStretchComponent, cls).create(meta_parent, side=side, name=name, tag=tag)  # type: IKStretchComponent
        instance.pynode.addAttr("state", at="message")
        instance.pynode.addAttr("threshold", at="message")

        # Create control attributes
        meta_parent.ik_control.transform.addAttr(toggle_attr_name, at="bool", k=1, dv=default_state)
        meta_parent.ik_control.transform.addAttr(threshold_attr_name, at="float", k=1, dv=threshold)
        meta_parent.ik_control.transform.attr(toggle_attr_name).connect(instance.pynode.state)
        meta_parent.ik_control.transform.attr(threshold_attr_name).connect(instance.pynode.threshold)

        # Stretch setup
        distance_node = nodeFn.create("distanceBetween", [instance.indexed_name, "diff"], instance.side, suffix="dst")  # type: luna_rig.nt.DistanceBetween
        meta_parent.group_joints_offset.worldMatrix.connect(distance_node.inMatrix1)
        meta_parent.ik_control.transform.worldMatrix.connect(distance_node.inMatrix2)

        divide_value_node = nodeFn.create("multiplyDivide", [instance.indexed_name, "value"], instance.side, suffix="mdv")
        divide_value_node.operation.set(2)
        distance_node.distance.connect(divide_value_node.input1X)
        divide_value_node.input2X.set(distance_node.distance.get())

        # Threshold
        threshold_add = nodeFn.create("addDoubleLinear", [instance.indexed_name, "threshold"], instance.side, suffix="adl")
        threshold_add.input1.set(distance_node.distance.get())
        meta_parent.ik_control.transform.attr(threshold_attr_name).connect(threshold_add.input2)

        # Scaled mdl
        scaled_mdl = nodeFn.create("multDoubleLinear", [instance.indexed_name, "scaled"], instance.side, suffix="mdl")
        if meta_parent.character:
            meta_parent.character.root_control.transform.Scale.connect(scaled_mdl.input1)
        else:
            Logger.warning("{0}: metaparent {1} is missing character connections. Scaling might behave incorrect")
            scaled_mdl.input1.set(1.0)
        threshold_add.output.connect(scaled_mdl.input2)
        scaled_mdl.output.connect(divide_value_node.input2X)

        # Toggle mdl
        toggle_mdl = nodeFn.create("multDoubleLinear", [instance.indexed_name, "toggle"], instance.side, suffix="mdl")
        # divide_value_node
        divide_value_node.outputX.connect(toggle_mdl.input1)
        meta_parent.ik_control.transform.attr(toggle_attr_name).connect(toggle_mdl.input2)

        # Condition
        condition = nodeFn.create("condition", [instance.indexed_name, "rule"], instance.side, suffix="cond")
        condition.secondTerm.set(1.0)
        condition.operation.set(2)
        toggle_mdl.output.connect(condition.firstTerm)
        toggle_mdl.output.connect(condition.colorIfTrueR)

        # Connect to joints
        for ctl_jnt in meta_parent.ctl_chain[:-1]:
            condition.outColorR.connect(ctl_jnt.attr("s{0}".format(stretch_axis)))

        # Handle twist components
        twist_joints = []
        for twist_comp in meta_parent.get_meta_children(of_type=luna_rig.components.TwistComponent):
            twist_joints += twist_comp.ctl_chain[:-1]
        for twst_jnt in twist_joints:
            condition.outColorR.connect(twst_jnt.attr("s{0}".format(stretch_axis)))

        # Store settings
        instance._store_settings(meta_parent.ik_control.transform.attr(toggle_attr_name))
        instance._store_settings(meta_parent.ik_control.transform.attr(threshold_attr_name))

        return instance

    def remove(self):
        self.state = False
        self._delete_settings_attrs()
        super(IKStretchComponent, self).remove()
