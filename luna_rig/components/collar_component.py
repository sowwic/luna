import pymel.core as pm
from pymel.core import datatypes
import luna_rig
from luna import Logger
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.transformFn as transformFn
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.functions.cmuscleFn as cmuscleFn


class CollarComponent(luna_rig.AnimComponent):
    """Collar like joint based component with collision setup."""

    required_plugins = ["MayaMuscle"]

    @classmethod
    def create(cls,
               curve,
               collision_mesh,
               meta_parent=None,
               side="c",
               name="collar",
               hook=None,
               character=None,
               tag="",
               num_controls=8,
               skel_joint_parent=None):
        # type: (str, str, luna_rig.AnimComponent, str, str, int, luna_rig.Character, str, int, str) -> CollarComponent

        # Parse arguments
        if not isinstance(curve, pm.PyNode):
            curve = pm.PyNode(curve)  # type: luna_rig.nt.Transform
        if not isinstance(collision_mesh, pm.PyNode):
            collision_mesh = pm.PyNode(collision_mesh)  # type: luna_rig.nt.Transform

        instance = super(CollarComponent, cls).create(meta_parent=meta_parent, side=side, name=name, hook=hook, character=character, tag=tag)
        pm.parent(curve, instance.group_noscale)

        # Create collision clusters
        cluster_grp = nodeFn.create('transform',
                                    [instance.indexed_name, 'cluster'],
                                    instance.side,
                                    suffix='grp',
                                    parent=instance.group_parts)  # type: luna_rig.nt.Transform
        collision_clusters = []
        cluster_ofs_groups = []
        count = 0
        for cv_index in range(0, curve.getShape().numCVs()):
            count += 1
            cluster = pm.cluster(curve.cv[cv_index], n=nameFn.generate_name([instance.indexed_name, "collision"], side=instance.side, suffix="clst"))
            clst_offset_grp = pm.group(cluster, n=nameFn.generate_name([instance.indexed_name, 'clst', 'offs'],
                                                                       side=instance.side,
                                                                       suffix="grp"))  # type: luna_rig.nt.Transform
            pm.matchTransform(clst_offset_grp, cluster)
            pm.parent(clst_offset_grp, cluster_grp)
            collision_clusters.append(cluster)
            cluster_ofs_groups.append(clst_offset_grp)

        # Setup collision mesh
        cmuscleFn.make_cmuscle(collision_mesh)
        muscle_keepout_nodes = cmuscleFn.rig_keepout(cluster_ofs_groups)

        # Get clusters relative position to collision mesh pivot.
        # Normalize it and use as push direction for collision.
        mesh_pos = transformFn.get_world_position(collision_mesh)
        for clst_trs, keepout_node in zip(cluster_ofs_groups, muscle_keepout_nodes):
            clst_pos = transformFn.get_world_position(clst_trs)
            mesh_to_clst_vec = clst_pos - mesh_pos  # type: datatypes.FloatVector
            mesh_to_clst_vec.normalize()

            keepout_node.getShape().inDirectionX.set(mesh_to_clst_vec.x)
            keepout_node.getShape().inDirectionY.set(mesh_to_clst_vec.y)
            keepout_node.getShape().inDirectionZ.set(mesh_to_clst_vec.z)

        cmuscleFn.connect_muscles_to_keepout(cluster_ofs_groups, collision_mesh)

        # Setup controls
        controls = []
        while len(controls) < num_controls:
            ctl = luna_rig.Control.create(name=[instance.indexed_name, 'shape'],
                                          side=instance.side,
                                          guide=None,
                                          parent=instance.group_ctls,
                                          shape='joint')
            controls.append(ctl)

        transformFn.position_along_curve(curve, [ctl.group for ctl in controls])
        transformFn.attach_all_to_curve(curve,
                                        [ctl.group for ctl in controls],
                                        [instance.indexed_name, "info"],
                                        instance.side)

        # Setup bind joints
        bind_joints = []
        for ctl in controls:
            jnt = nodeFn.create('joint', [instance.indexed_name, "bind"], instance.side, suffix='jnt')
            pm.matchTransform(jnt, ctl.transform)
            pm.parentConstraint(ctl.transform, jnt)
            pm.parent(jnt, skel_joint_parent)
            bind_joints.append(jnt)
        attrFn.add_meta_attr(bind_joints)

        # Store data
        instance._store_bind_joints(bind_joints)
        instance._store_controls(controls)
        instance.connect_to_character(character, parent=True)
        instance.attach_to_component(meta_parent, hook)

        return instance

    def attach_to_component(self, other_comp, hook_index=None):
        super(CollarComponent, self).attach_to_component(other_comp, hook_index=hook_index)
        if self.in_hook:
            pm.parentConstraint(self.in_hook.transform, self.group_parts, mo=1)
