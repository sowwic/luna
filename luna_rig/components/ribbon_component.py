import pymel.core as pm
from luna import Logger
import luna_rig
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.rivetFn as rivetFn


class RibbonComponent(luna_rig.AnimComponent):

    @property
    def surface(self):
        return self.pynode.surface.get()

    @property
    def shape_controls(self):
        connected_nodes = self.pynode.shapeControls.listConnections()  # type: list[luna_rig.nt.Transform]
        all_ctls = [luna_rig.Control(node) for node in connected_nodes]
        return all_ctls

    @property
    def main_control(self):
        transform = self.pynode.mainControl.get()
        if not transform:
            return None
        else:
            return luna_rig.Control(transform)

    @property
    def is_fk(self):
        return self.pynode.fkHierarchy.get()

    # ========== Getter methods =============== #

    def get_surface(self):
        return self.surface

    def get_shape_controls(self):
        return self.shape_controls

    def get_main_control(self):
        return self.main_control

    def get_is_fk(self):
        return self.is_fk

    @classmethod
    def create(cls,
               character=None,
               meta_parent=None,
               hook=0,
               side='c',
               name='ribbon',
               surface=None,
               num_controls=3,
               skel_joint_parent=None,
               single_joint_hierarchy=False,
               use_span="u",
               fk_hierarchy=False,
               override_num_rivets=0,
               flip_rivets_normal=False,
               tag=""):
        # Parse arguments
        num_controls = int(num_controls) if not isinstance(num_controls, int) else num_controls
        override_num_rivets = int(override_num_rivets) if not isinstance(override_num_rivets, int) else override_num_rivets

        # Metanode attributes
        instance = super(RibbonComponent, cls).create(meta_parent=meta_parent, side=side, name=name, hook=hook, character=character, tag=tag)  # type: RibbonComponent
        instance.pynode.addAttr("surface", at="message")
        instance.pynode.addAttr("fkHierarchy", at="bool", dv=fk_hierarchy, w=False, r=True)
        instance.pynode.fkHierarchy.lock()
        instance.pynode.addAttr("shapeControls", at="message", multi=True, im=False)
        instance.pynode.addAttr("mainControl", at="message")

        # Validate surface
        if not surface:
            Logger.exception("{0}: component requires NURBS surface for creation.".format(instance))
            raise ValueError
        if not isinstance(surface, pm.PyNode):
            surface = pm.PyNode(surface)  # type: luna_rig.nt.Transform
        if not isinstance(surface.getShape(), luna_rig.nt.NurbsSurface):
            Logger.exception("{0}: object {1} is not a NURBS surface".format(instance, surface))
            raise TypeError
        attrFn.add_meta_attr(surface)
        surface.setParent(instance.group_noscale)

        # Ctl chain
        rivets = rivetFn.FollicleRivet.along_surface(surface,
                                                     side=instance.side,
                                                     name=[instance.indexed_name, "rivet"],
                                                     use_span=use_span,
                                                     parent=instance.group_noscale,
                                                     amount=override_num_rivets,
                                                     flip_direction=flip_rivets_normal)
        ctl_chain = []
        for follicle in rivets:
            ctl_jnt = nodeFn.create("joint", [instance.indexed_name, "ctl"], instance.side, "jnt", parent=follicle.transform)
            ctl_chain.append(ctl_jnt)

        # Shape controls
        shape_controls = []
        guide_rivets = rivetFn.FollicleRivet.along_surface(surface,
                                                           side=instance.side,
                                                           name=[instance.indexed_name, "guide_rivet"],
                                                           use_span=use_span,
                                                           parent=None,
                                                           amount=num_controls,
                                                           flip_direction=flip_rivets_normal)
        for guide_rvt in guide_rivets:
            shape_ctl = luna_rig.Control.create(name=[instance.indexed_name, "shape"],
                                                side=instance.side,
                                                guide=guide_rvt.transform,
                                                delete_guide=True,
                                                parent=instance.group_ctls,
                                                joint=True,
                                                shape="circle",
                                                tag="shape")
            shape_controls.append(shape_ctl)
        pm.skinCluster([ctl.joint for ctl in shape_controls], surface)
        if fk_hierarchy:
            for ctl_index in range(len(shape_controls) - 1):
                shape_controls[ctl_index + 1].set_parent(shape_controls[ctl_index])

        # Output joints
        bind_joints = []
        for ctl_jnt in ctl_chain:
            bind_jnt = nodeFn.create("joint", instance.name, instance.side, suffix="jnt")
            pm.matchTransform(bind_jnt, ctl_jnt)
            if single_joint_hierarchy and bind_joints:
                bind_jnt.setParent(bind_joints[-1])
            bind_joints.append(bind_jnt)

        # Parent into main skeleton
        if not single_joint_hierarchy:
            joints_to_parent = bind_joints
        else:
            joints_to_parent = [bind_joints[0]]

        if skel_joint_parent:
            for jnt in joints_to_parent:
                jnt.setParent(skel_joint_parent)
        else:
            joints_to_parent[0].setParent(instance.group_joints)

        # Store objects
        surface.metaParent.connect(instance.pynode.surface)
        for shape_ctl in shape_controls:
            shape_ctl.transform.metaParent.connect(instance.pynode.shapeControls, na=True)
        instance._store_bind_joints(bind_joints)
        instance._store_ctl_chain(ctl_chain)
        instance._store_controls(shape_controls)

        # Attach
        instance.attach_to_component(meta_parent, hook_index=hook)
        instance.connect_to_character(character_component=character, parent=True)

        # Scale controls
        scale_dict = {}
        for ctl in shape_controls:
            scale_dict[ctl] = 0.06
        instance.scale_controls(scale_dict)

        # Housekeeping
        instance.group_joints.visibility.set(False)
        instance.group_parts.visibility.set(False)

        return instance

    def add_main_control(self, guide):
        main_ctl = luna_rig.Control.create(name=[self.indexed_name, "main"],
                                           side=self.side,
                                           guide=guide,
                                           delete_guide=True,
                                           attributes="trs",
                                           shape="circle",
                                           orient_axis="z",
                                           parent=self.group_ctls)
        # Parent shape controls
        if self.is_fk:
            self.shape_controls[0].set_parent(main_ctl)
        else:
            for shp_ctl in self.shape_controls:
                shp_ctl.set_parent(main_ctl)

        self._store_controls([main_ctl])

        # Scale control
        scale_dict = {main_ctl: 0.06}
        self.scale_controls(scale_dict)
        return main_ctl

    def attach_to_skeleton(self):
        super(RibbonComponent, self).attach_to_skeleton()
        for ctl_jnt, bind_jnt in zip(self.ctl_chain, self.bind_joints):
            pm.scaleConstraint(ctl_jnt, bind_jnt)

    def attach_to_component(self, other_comp, hook_index=None):
        super(RibbonComponent, self).attach_to_component(other_comp, hook_index=hook_index)
        if self.in_hook:
            pm.parentConstraint(self.in_hook.transform, self.group_ctls, mo=1)
