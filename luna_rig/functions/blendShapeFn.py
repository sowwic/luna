import pymel.core as pm
import luna_rig
from luna import Logger


# Based on bSpiritCorrective MEL script
class Corrective:
    def __init__(self, pose_mesh, base_mesh):
        # Initialize data
        self.pose_mesh = pm.PyNode(pose_mesh)  # type: luna_rig.nt.Transform
        self.base_mesh = pm.PyNode(base_mesh)  # type: luna_rig.nt.Transform
        self.output_mesh = None  # type: luna_rig.nt.Transform

        # Base mesh skin nodes
        self.skin_clusters = self.base_mesh.listHistory(type="skinCluster")  # type: list
        self.tweaks = self.base_mesh.listHistory(type="tweak")  # type: list
        if not self.skin_clusters or not self.tweaks:
            Logger.error("Corrective: No skin cluster/tweaks found for {0}".format(self.base_mesh))
            raise ValueError

        # Vertex count and names
        # ? Might be better to use world position instead
        self.offset = self.pose_mesh.translate.get() - self.base_mesh.translate.get()
        self.base_mesh_vtx_count = pm.polyEvaluate(self.base_mesh, v=1)  # type: int
        self.pose_mesh_vtx_count = pm.polyEvaluate(self.pose_mesh, v=1)  # type: int
        if not self.base_mesh_vtx_count == self.pose_mesh_vtx_count:
            Logger.error("Corrective: Vtx count of {0} is not identical to {1}".format(self.base_mesh, self.pose_mesh))
            raise ValueError

        self.tweak_vtx_array = []
        self.vtx_name_array = []
        self.selected_vtx_number_array = []
        self.target_positions_array = []
        self.abs_positions_array = []
        self.rel_positions_array = []
        self._get_vtx_data()

    def _vector_move(self, tweak_vtx_name, base_mesh_vtx_name,
                     world_posx, world_posy, world_posz,
                     target_posx, target_posy, target_posz,
                     rel_posx, rel_posy, rel_posz):
        temp_pos = [0.0, 0.0, 0.0]
        matrix = [0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0]
        pm.setAttr("{}.xVertex".format(tweak_vtx_name), rel_posx + 1)
        temp_pos = pm.pointPosition(base_mesh_vtx_name, w=1)
        matrix[0] = temp_pos[0] - world_posx
        matrix[4] = temp_pos[1] - world_posy
        matrix[8] = temp_pos[2] - world_posz
        matrix[3] = target_posx

        pm.setAttr("{}.xVertex".format(tweak_vtx_name), rel_posx)
        pm.setAttr("{}.yVertex".format(tweak_vtx_name), rel_posy + 1)
        temp_pos = pm.pointPosition(base_mesh_vtx_name, w=1)
        matrix[1] = temp_pos[0] - world_posx
        matrix[5] = temp_pos[1] - world_posy
        matrix[9] = temp_pos[2] - world_posz
        matrix[7] = target_posy

        pm.setAttr("{}.yVertex".format(tweak_vtx_name), rel_posy)
        pm.setAttr("{}.zVertex".format(tweak_vtx_name), rel_posz + 1)
        temp_pos = pm.pointPosition(base_mesh_vtx_name, w=1)
        matrix[2] = temp_pos[0] - world_posx
        matrix[6] = temp_pos[1] - world_posy
        matrix[10] = temp_pos[2] - world_posz
        matrix[11] = target_posz

        freturn = [0.0, 0.0, 0.0]
        fDenominator = (matrix[0] * ((matrix[5] * matrix[10]) - (matrix[6] * matrix[9]))) - \
            (matrix[1] * ((matrix[4] * matrix[10]) - (matrix[6] * matrix[8]))) + \
            (matrix[2] * ((matrix[4] * matrix[9]) - (matrix[5] * matrix[8])))

        if fDenominator:
            freturn[0] = (
                (matrix[3] * ((matrix[5] * matrix[10]) - (matrix[6] * matrix[9]))) -
                (matrix[1] * ((matrix[7] * matrix[10]) - (matrix[6] * matrix[11]))) +
                (matrix[2] * ((matrix[7] * matrix[9]) - (matrix[5] * matrix[11])))
            ) / fDenominator

            freturn[1] = (
                (matrix[0] * ((matrix[7] * matrix[10]) - (matrix[6] * matrix[11]))) -
                (matrix[3] * ((matrix[4] * matrix[10]) - (matrix[6] * matrix[8]))) +
                (matrix[2] * ((matrix[4] * matrix[11]) - (matrix[7] * matrix[8])))
            ) / fDenominator

            freturn[2] = (
                (matrix[0] * ((matrix[5] * matrix[11]) - (matrix[7] * matrix[9]))) -
                (matrix[1] * ((matrix[4] * matrix[11]) - (matrix[7] * matrix[8]))) +
                (matrix[3] * ((matrix[4] * matrix[9]) - (matrix[5] * matrix[8])))
            ) / fDenominator

            pm.setAttr("{}.xVertex".format(tweak_vtx_name), rel_posx + freturn[0])
            pm.setAttr("{}.yVertex".format(tweak_vtx_name), rel_posy + freturn[1])
            pm.setAttr("{}.zVertex".format(tweak_vtx_name), rel_posz + freturn[2])

    def _get_position(self, pose_shape_vtx_name, base_mesh_vtx_name, offset_x, offset_y, offset_z):
        target_position = pm.pointPosition(pose_shape_vtx_name, w=1)
        pt_pos = pm.pointPosition(base_mesh_vtx_name, w=1)
        rel_vtx_position = pm.getAttr(base_mesh_vtx_name)

        target_position[0] -= pt_pos[0] + offset_x
        target_position[1] -= pt_pos[1] + offset_y
        target_position[2] -= pt_pos[2] + offset_z

        result = [-1.0]
        if ((target_position[0] > 0.001 or target_position[0] < -0.001) or
            (target_position[1] > 0.001 or target_position[1] < -0.001) or
                (target_position[2] > 0.001 or target_position[2] < -0.001)):
            result = [1.0,
                      pt_pos[0], pt_pos[1], pt_pos[2],
                      target_position[0], target_position[1], target_position[2],
                      rel_vtx_position[0], rel_vtx_position[1], rel_vtx_position[2]]
        return result

    def _get_vtx_data(self):
        for index in range(0, self.base_mesh_vtx_count):
            self.selected_vtx_number_array.append(index)

            vtx_appendix = ".vtx[{0}]".format(self.selected_vtx_number_array[index])
            base_mesh_vtx_name = str(self.base_mesh) + vtx_appendix
            pose_mesh_vtx_name = str(self.pose_mesh) + vtx_appendix

            # Get position
            positions_array = self._get_position(pose_mesh_vtx_name, base_mesh_vtx_name,
                                                 self.offset[0], self.offset[1], self.offset[2])

            # Fill move arrays data
            if positions_array[0] == 1:
                self.vtx_name_array.append(base_mesh_vtx_name)
                self.tweak_vtx_array.append("{0}.vlist[0].vertex[{1}]".format(str(self.tweaks[0]), self.selected_vtx_number_array[index]))

                self.abs_positions_array.append(positions_array[1])
                self.abs_positions_array.append(positions_array[2])
                self.abs_positions_array.append(positions_array[3])

                self.target_positions_array.append(positions_array[4])
                self.target_positions_array.append(positions_array[5])
                self.target_positions_array.append(positions_array[6])

                self.rel_positions_array.append(positions_array[7])
                self.rel_positions_array.append(positions_array[8])
                self.rel_positions_array.append(positions_array[9])

    def _duplicate_mesh(self):
        for skin in self.skin_clusters:
            skin.nodeState.set(1)
        for bs_node in pm.listHistory(self.base_mesh, type="blendShape"):
            bs_node.nodeState.set(1)

        self.output_mesh = pm.duplicate(self.base_mesh, rr=1, rc=1)[0]
        for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
            pm.setAttr(self.output_mesh.attr(attr), lock=0)

    def _reset_base_mesh(self):
        for i in range(0, len(self.vtx_name_array)):
            array_index = i * 3
            pm.setAttr(self.tweak_vtx_array[array_index / 3] + ".xVertex", self.rel_positions_array[array_index])
            pm.setAttr(self.tweak_vtx_array[array_index / 3] + ".yVertex", self.rel_positions_array[array_index + 1])
            pm.setAttr(self.tweak_vtx_array[array_index / 3] + ".zVertex", self.rel_positions_array[array_index + 2])

        for skin in self.skin_clusters:
            skin.nodeState.set(0)
        for bs in pm.listHistory(self.base_mesh, type="blendShape"):
            bs.nodeState.set(0)

    @classmethod
    def generate(cls, pose_mesh, base_mesh, parent=None, name=None):
        instance = cls(pose_mesh, base_mesh)
        Logger.info("Gathering verticies to move...")
        if len(instance.vtx_name_array) > 0:
            percent_moved = 0.5 + float(len(instance.vtx_name_array)) / float(instance.base_mesh_vtx_count) * 100.0
        else:
            Logger.warning("Not enought delta between {0} and {1} for corrective.".format(instance.base_mesh, instance.pose_mesh))
            return

        Logger.info("Generating new shape...")
        # Calculate vertex matrix and move
        for index in range(0, len(instance.vtx_name_array)):
            array_pos = index * 3
            instance._vector_move(instance.tweak_vtx_array[array_pos / 3], instance.vtx_name_array[array_pos / 3],
                                  instance.abs_positions_array[array_pos], instance.abs_positions_array[array_pos + 1], instance.abs_positions_array[array_pos + 2],
                                  instance.target_positions_array[array_pos], instance.target_positions_array[array_pos + 1], instance.target_positions_array[array_pos + 2],
                                  instance.rel_positions_array[array_pos], instance.rel_positions_array[array_pos + 1], instance.rel_positions_array[array_pos + 2])
        # Get resulting shape
        instance._duplicate_mesh()
        instance._reset_base_mesh()
        if name:
            instance.output_mesh.rename(name)
        if parent:
            instance.output_mesh.setParent(parent)
        Logger.info("Generated corrective shape (delta {0}% ) : {1}".format(percent_moved, instance.output_mesh))
        return instance
