from collections import OrderedDict
import luna_builder.editor.editor_conf as editor_conf


def get_item_from_list(in_list, index):
    return in_list[int(index)]


def register_plugin():
    editor_conf.register_function(get_item_from_list,
                                  editor_conf.DataType.LIST,
                                  inputs_dict=OrderedDict([
                                      ('List', editor_conf.DataType.LIST),
                                      ('Index', editor_conf.DataType.NUMERIC)]),
                                  outputs_dict={'Item': editor_conf.DataType.STRING},
                                  default_values=[[], 0],
                                  nice_name='Get String',
                                  subtype='string',
                                  category='List')

    editor_conf.register_function(get_item_from_list,
                                  editor_conf.DataType.LIST,
                                  inputs_dict=OrderedDict([
                                      ('List', editor_conf.DataType.LIST),
                                      ('Index', editor_conf.DataType.NUMERIC)]),
                                  outputs_dict={'Item': editor_conf.DataType.CONTROL},
                                  default_values=[[], 0],
                                  nice_name='Get Control',
                                  subtype='control',
                                  category='List')

    editor_conf.register_function(get_item_from_list,
                                  editor_conf.DataType.LIST,
                                  inputs_dict=OrderedDict([
                                      ('List', editor_conf.DataType.LIST),
                                      ('Index', editor_conf.DataType.NUMERIC)]),
                                  outputs_dict={'Item': editor_conf.DataType.COMPONENT},
                                  default_values=[[], 0],
                                  nice_name='Get Component',
                                  subtype='component',
                                  category='List')

    editor_conf.register_function(get_item_from_list,
                                  editor_conf.DataType.LIST,
                                  inputs_dict=OrderedDict([
                                      ('List', editor_conf.DataType.LIST),
                                      ('Index', editor_conf.DataType.NUMERIC)]),
                                  outputs_dict={'Item': editor_conf.DataType.ANIM_COMPONENT},
                                  default_values=[[], 0],
                                  nice_name='Get AnimComponent',
                                  subtype='animcomponent',
                                  category='List')
