import os
import unittest
import pymel.core as pm
from Luna.workspace.asset import Asset
from Luna.workspace.project import Project
from Luna.utils import environFn
from Luna.utils import fileFn
from Luna.static import Directories
from Luna.test import TestCase


class AssetTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super(AssetTests, cls).tearDownClass()
        Project.exit()
        Project.refresh_recent()

    @staticmethod
    def patch_find_model(*args):
        """
        Override find_model file to avoid QFileDialog call.
        Return test model path instead
        """
        model_path = os.path.join(Directories.LUNA_ROOT_PATH, "tests", "util_files", "mannequin_model.ma")
        return os.path.normpath(model_path)

    def test_asset_ctor(self):
        asset_type = "character"

        creation_path = AssetTests.get_temp_dirname("testProject")
        test_project = Project.create(creation_path)
        Asset.find_model = self.patch_find_model
        test_asset = Asset("testAsset", typ=asset_type)

        # Base Assertions
        self.assertTrue(os.path.isdir(test_asset.path))  # Asset folder created
        self.assertTrue(os.path.isfile(test_asset.meta_path))  # Meta data file created
        self.assertEqual(test_asset.name, "testAsset")  # Asset name is stored
        self.assertTrue(os.path.isdir(os.path.join(test_project.path, asset_type + "s")))  # Asset category folder is created
        # Check asset folders creations
        self.assertTrue(os.path.isdir(test_asset.controls))
        self.assertTrue(os.path.isdir(test_asset.guides))
        self.assertTrue(os.path.isdir(test_asset.rig))
        self.assertTrue(os.path.isdir(test_asset.settings))
        self.assertTrue(os.path.isdir(test_asset.weights.blend_shape))
        self.assertTrue(os.path.isdir(test_asset.weights.delta_mush))
        self.assertTrue(os.path.isdir(test_asset.weights.dsAttract))
        self.assertTrue(os.path.isdir(test_asset.weights.ffd))
        self.assertTrue(os.path.isdir(test_asset.weights.ncloth))
        self.assertTrue(os.path.isdir(test_asset.weights.ng_layers))
        self.assertTrue(os.path.isdir(test_asset.weights.non_linear))
        self.assertTrue(os.path.isdir(test_asset.weights.skin_cluster))
        self.assertTrue(os.path.isdir(test_asset.weights.soft_mod))
        self.assertTrue(os.path.isdir(test_asset.weights.tension))
        self.assertTrue(os.path.isdir(test_asset.data.blend_shapes))
        self.assertTrue(os.path.isdir(test_asset.data.mocap))
        self.assertTrue(os.path.isdir(test_asset.data.poses))
        self.assertTrue(os.path.isdir(test_asset.data.xgen))
        # Template files creation
        self.assertTrue(os.path.isfile(os.path.join(test_asset.guides, "{0}_guides.0000.ma".format(test_asset.name))))
        self.assertTrue(os.path.isfile(os.path.join(test_asset.rig, "{0}_rig.0000.ma".format(test_asset.name))))


if __name__ == "__main__":
    unittest.main(exit=False)
