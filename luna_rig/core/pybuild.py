import pymel.core as pm
import timeit

from luna import Logger
import luna.workspace
import luna_rig
import luna.utils.maya_utils as maya_utils
import luna_rig.functions.asset_files as asset_files


class PyBuild(object):
    def __init__(self, asset_type, asset_name, existing_character=None):

        # Get project instance
        self.project = luna.workspace.Project.get()
        if not self.project:
            pm.warning("Project is not set!")
            return

        # Start build
        pm.scriptEditorInfo(e=1, sr=1)
        pm.newFile(f=1)
        self.start_time = timeit.default_timer()
        Logger.info("Initiating new build...")

        self.asset = luna.workspace.Asset(self.project, asset_name, asset_type)
        # Import model and componets files
        asset_files.import_model()
        asset_files.import_skeleton()
        # Setup character
        if existing_character:
            self.character = luna_rig.components.Character(existing_character)
        else:
            self.character = luna_rig.components.Character.create(name=asset_name)

        # Override methods
        self.run()
        self.character.save_bind_pose()
        Logger.info("Running post build tasks...")
        self.post()

        # Adjust viewport
        pm.select(cl=1)
        maya_utils.switch_xray_joints()
        pm.viewFit(self.character.root_control.group)
        self.character.geometry_grp.overrideEnabled.set(1)
        self.character.geometry_grp.overrideColor.set(1)

        # Report completion
        Logger.info("Build finished in {0:.2f}s".format(timeit.default_timer() - self.start_time))
        pm.scriptEditorInfo(e=1, sr=0)

    def run(self):
        pass

    def post(self):
        pass
