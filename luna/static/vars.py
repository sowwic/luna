class LunaVars:
    logging_level = "logging.level"
    command_port = "python.commandPort"
    callback_licence = "callback.license"
    naming_templates = "naming.templates"
    naming_profile = "naming.profile"


class HudVars:
    block = "hud.block"
    section = "hud.section"


class TestVars:
    delete_files = "tests.delete_files"
    delete_dirs = "tests.delete_dirs"
    temp_dir = "tests.temp_dir"
    buffer_output = "tests.buffer_output"
    new_file = "tests.new_file"


class ProjectVars:
    recent_projects = "project.recent"
    previous_project = "project.previous"
    recent_max = "project.max_recent"


class BuildVars:
    geometry_override = "build.geometry.overrideEnabled"


class UnrealVars:
    project = "unreal.project"
    anim_dir = "unreal.animations"
    mesh_dir = "unreal.meshes"


class AnimExporterVars:
    prorerties_root = "animexporter"
    bake_on_remove = "animexporter.bakeOnRemove"
    minimize_rotation = "animexporter.minimizeRotation"
    simulation = "animexporter.simulation"
    keep_unbacked_keys = "animexporter.keepUnbackedKeys"
    sparce_curve_bake = "animexporter.sparceCurveBake"
    disable_implicit = "animexporter.disableImplicitControl"
    unroll_rotation = "animexporter.unrollRotation"
    sample_by = "animexporter.sample"
    oversample_rate = "animexporter.oversampleRate"
    increase_fidelity = "animexporter.increaseFidelity"
    fidelity_keys_tol = "animexporter.fidelityKeysTolerance"
    smart_bake = "animexporter.smartBake"
