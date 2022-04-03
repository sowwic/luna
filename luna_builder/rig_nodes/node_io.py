
import sys
import luna_rig.importexport as import_export
import luna_builder.editor.editor_conf as editor_conf


def register_plugin():
    editor_conf.register_function(import_export.SkinManager.import_all,
                                  None,
                                  nice_name='Import Skin Weights',
                                  category='Data')
    editor_conf.register_function(import_export.NgLayers2Manager.import_all,
                                  None,
                                  nice_name='Import NgLayers2',
                                  category='Data')
    editor_conf.register_function(import_export.CtlShapeManager.import_asset_shapes,
                                  None,
                                  nice_name='Import Control Shapes',
                                  category='Data')
    editor_conf.register_function(import_export.BlendShapeManager.import_all,
                                  None,
                                  nice_name='Import BlendShapes',
                                  category='Data')
    editor_conf.register_function(import_export.DrivenPoseManager.import_all,
                                  None,
                                  nice_name='Import Driven Poses',
                                  category='Data')
    editor_conf.register_function(import_export.PsdManager.import_all,
                                  None,
                                  nice_name='Import PSD',
                                  category='Data')
    editor_conf.register_function(import_export.SDKCorrectiveManager.import_all,
                                  None,
                                  nice_name='Import SDK Correctives',
                                  category='Data')
    editor_conf.register_function(import_export.DeltaMushManager.import_all,
                                  None,
                                  inputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  nice_name='Import DeltaMush',
                                  category='Data')

    if sys.version_info[0] < 3:
        editor_conf.register_function(import_export.NgLayersManager.import_all,
                                      None,
                                      nice_name='Import NgLayers',
                                      category='Data')
