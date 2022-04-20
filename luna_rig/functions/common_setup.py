import luna_rig
import pymel.core as pm

MATRIX_NODES_AVAILABLE = int(pm.about(version=True)) > 2020


def basic_limbs_spaces(arm_components=None,  # type: list[luna_rig.components.FKIKComponent]
                       leg_components=None,  # type: list[luna_rig.components.FKIKComponent]
                       spine=None,  # type: luna_rig.components.FKIKSpineComponent
                       ):
    # type: (...) -> None
    """Add commond limb spaces

    Args:
        arm_components (list[luna_rig.components.FKIKComponent], optional): Arm FKIK components. Defaults to None.
        leg_components (list[luna_rig.components.FKIKComponent], optional): Leg FKIK components. Defaults to None.
        spine (luna_rig.components.FKIKSpineComponent, optional): Spine component. Defaults to None.
    """

    # Add fk orient switches
    character = None
    for arm in arm_components:
        character = character if character else arm.character
        # Pole vector
        arm.pv_control.add_world_space(via_matrix=MATRIX_NODES_AVAILABLE)
        arm.pv_control.add_space(arm.ik_control, "IK", via_matrix=MATRIX_NODES_AVAILABLE)
        if spine:
            arm.pv_control.add_space(spine.chest_control, "Chest",
                                     via_matrix=MATRIX_NODES_AVAILABLE)
            arm.pv_control.add_space(spine.hips_control, "Hips", via_matrix=MATRIX_NODES_AVAILABLE)
        # IK
        arm.ik_control.add_world_space(via_matrix=MATRIX_NODES_AVAILABLE)
        if spine:
            arm.ik_control.add_space(spine.chest_control, "Chest",
                                     via_matrix=MATRIX_NODES_AVAILABLE)
            arm.ik_control.add_space(spine.hips_control, "Hips", via_matrix=MATRIX_NODES_AVAILABLE)

    for leg in leg_components:
        character = character if character else leg.character
        leg.pv_control.add_world_space(via_matrix=MATRIX_NODES_AVAILABLE)
        leg.pv_control.add_space(leg.ik_control, "IK", via_matrix=MATRIX_NODES_AVAILABLE)
        if spine:
            leg.pv_control.add_space(spine.hips_control, "Hips", via_matrix=MATRIX_NODES_AVAILABLE)
        leg.ik_control.add_world_space(via_matrix=MATRIX_NODES_AVAILABLE)
        if spine:
            leg.ik_control.add_space(spine.hips_control, "Hips", via_matrix=MATRIX_NODES_AVAILABLE)
