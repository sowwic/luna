class LunaVars:
    logging_level = "logging.level"
    command_port = "python.commandPort"
    callback_licence = "callback.license"


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


class NamingVars:
    templates_dict = "naming.templates"
    current_template = "naming.profile.template"
    index_padding = "naming.profile.indexPadding"
    start_index = "naming.profile.startIndex"


class RigVars:
    skin_export_format = "rig.io.skin.fileFormat"
    nglayers_export_format = "rig.io.nglayers.fileFormat"
