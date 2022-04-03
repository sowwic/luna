import os
import imp
import numbers

from collections import OrderedDict
from PySide2 import QtCore
from PySide2 import QtGui

from luna import Logger
import luna_rig
import luna.static.directories as directories


# ====== CONSTANTS ======== #
PALETTE_MIMETYPE = 'luna/x-node-palette_item'
VARS_MIMETYPE = 'luna/x-vars_item'
UNBOUND_FUNCTION_DATATYPE = 'UNBOUND'
INTERNAL_CATEGORY = 'INTERNAL'
FUNC_NODE_ID = 100
INPUT_NODE_ID = 101
OUTPUT_NODE_ID = 102
SET_NODE_ID = 103
GET_NODE_ID = 104

# ====== EXCEPTIONS ======== #


class ConfException(Exception):
    pass


class InvalidNodeRegistration(ConfException):
    pass


class InvalidDataTypeRegistration(ConfException):
    pass


class NodeIDNotFound(ConfException):
    pass


# ====== QUEUES ======== #
NODES_QUEUE = OrderedDict()
FUNCTIONS_QUEUE = OrderedDict()

# ====== REGISTERS ======== #
DATATYPE_REGISTER = {}
NODE_REGISTER = {}
FUNCTION_REGISTER = {}


def instancer(cls):
    return cls()


@instancer
class DataType(object):

    EXEC = {'class': type(None),
            'color': QtGui.QColor("#FFFFFF"),
            'label': '',
            'default': None}
    STRING = {'class': str,
              'color': QtGui.QColor("#A203F2"),
              'label': 'Name',
              'default': ''}
    NUMERIC = {'class': numbers.Complex,
               'color': QtGui.QColor("#DEC017"),
               'label': 'Number',
               'default': 0.0}
    BOOLEAN = {'class': bool,
               'color': QtGui.QColor("#C40000"),
               'label': 'Condition',
               'default': False}
    LIST = {'class': list,
            'color': QtGui.QColor("#0BC8F1"),
            'label': 'List',
            'default': []}
    CONTROL = {'class': luna_rig.Control,
               'color': QtGui.QColor("#2BB12D"),
               'label': 'Control',
               'default': None}
    COMPONENT = {'class': luna_rig.Component,
                 'color': QtGui.QColor("#6495ED"),
                 'label': 'Component',
                 'default': None}
    ANIM_COMPONENT = {'class': luna_rig.AnimComponent,
                      'color': QtGui.QColor("#6495ED"),
                      'label': 'AnimComponent',
                      'default': None}
    CHARACTER = {'class': luna_rig.components.Character,
                 'color': QtGui.QColor("#5767FF"),
                 'label': 'Character',
                 'default': None}

    def __getattr__(self, name):
        if name in DATATYPE_REGISTER:
            return DATATYPE_REGISTER[name]
        else:
            Logger.error('Uregistered datatype: {0}'.format(name))
            raise KeyError

    @classmethod
    def _basic_types(cls):
        return [(dt, desc) for dt, desc in cls.__dict__.items() if isinstance(desc, dict)]

    @classmethod
    def _register_basic_types(cls):
        Logger.debug('Registering base datatypes')
        for type_name, type_dict in cls._basic_types():
            DATATYPE_REGISTER[type_name] = type_dict

    @ classmethod
    def register_datatype(cls, type_name, type_class, color, label='custom_data', default_value=None):
        if type_name in DATATYPE_REGISTER.keys():
            Logger.error('Datatype {0} is already registered'.format(type_name))
            raise InvalidDataTypeRegistration

        type_dict = {'class': type_class,
                     'color': color if isinstance(color, QtGui.QColor) else QtGui.QColor(color),
                     'label': label,
                     'default': default_value}
        DATATYPE_REGISTER[type_name.upper()] = type_dict

    @classmethod
    def runtime_types(cls, names=False, classes=False):
        result = []
        for type_name, type_desc in DATATYPE_REGISTER.items():
            if issubclass(type_desc['class'], (cls.COMPONENT['class'], cls.LIST['class'], cls.CONTROL['class'])):
                if names:
                    result.append(type_name)
                elif classes:
                    result.append(type_desc['class'])
                else:
                    result.append(DATATYPE_REGISTER[type_name])
        return result

    @classmethod
    def list_base_types(cls, of_type):
        basetypes = [typ for typ in DATATYPE_REGISTER.values() if issubclass(of_type, typ['class'])]
        return basetypes

    @classmethod
    def get_type_from_dataclass(cls, dataclass):
        for type_name, type_dict in DATATYPE_REGISTER.items():
            if type_dict['class'] == dataclass:
                return type_dict
        Logger.error('Failed to find registered data type for class {0}'.format(dataclass))
        raise ValueError

    @classmethod
    def get_type_name(cls, data_type_dict):
        try:
            type_name = [dt_name for dt_name, desc in DATATYPE_REGISTER.items() if desc ==
                         data_type_dict][0]
            return type_name
        except IndexError:
            Logger.exception('Failed to find datatype for class {0}'.format(
                data_type_dict['class']))
            raise IndexError

    @classmethod
    def get_type(cls, type_name):
        try:
            return DATATYPE_REGISTER[type_name]
        except KeyError:
            Logger.exception('Unregistered datatype: {0}'.format(type_name))
            raise


# ========== REGISTERS =========== #

def register_node(node_id, node_class):
    if node_id in NODES_QUEUE:
        Logger.error('Node with id {0} is already registered as {1}'.format(node_id, node_class))
        raise InvalidNodeRegistration
    NODES_QUEUE[node_id] = node_class


def _do_node_registrations():
    for node_id, node_class in NODES_QUEUE.items():
        NODE_REGISTER[node_id] = node_class
        Logger.debug('Registered node {0}::{1}'.format(node_id, node_class))
    NODES_QUEUE.clear()


def get_node_class_from_id(node_id):
    if node_id not in NODE_REGISTER:
        Logger.error('Node ID {0} was not found in register'.format(node_id))
        raise NodeIDNotFound
    return NODE_REGISTER[node_id]


def check_available_node_ids(start, end):
    for node_id in range(start, end):
        if node_id not in NODE_REGISTER.keys():
            Logger.info('Available ID: {0}'.format(node_id))


# ========== FUNCTIONS =========== #
def register_function(func,
                      source_datatype,
                      inputs_dict=None,
                      outputs_dict=None,
                      default_values=None,
                      nice_name=None,
                      subtype=None,
                      category='General',
                      docstring='',
                      icon='func.png'):
    # type: (function, dict, dict, dict, list, str, str, str, str, str) -> None
    inputs_dict = inputs_dict if inputs_dict is not None else dict()
    outputs_dict = outputs_dict if outputs_dict is not None else dict()
    default_values = default_values if default_values is not None else []

    # Get datatype index if source_datatype is not int
    if source_datatype:
        if isinstance(source_datatype, dict):
            dt_name = DataType.get_type_name(source_datatype)
        else:
            Logger.error(
                'Invalid datatype passed to register function: {0}'.format(source_datatype))
            raise ValueError
    else:
        dt_name = UNBOUND_FUNCTION_DATATYPE

    # Create register signature
    if source_datatype:
        src_class = source_datatype.get('class')
        if src_class:
            signature = "{0}.{1}.{2}".format(
                src_class.__module__, src_class.__name__, func.__name__)
        else:
            signature = "{0}.{1}".format(func.__module__, func.__name__)
    else:
        signature = "{0}.{1}".format(func.__module__, func.__name__)

    # Subtype signature
    if subtype:
        signature = '{0}({1})'.format(signature, subtype)

    # Create function description
    func_dict = {'ref': func,
                 'inputs': inputs_dict,
                 'outputs': outputs_dict,
                 'doc': docstring,
                 'icon': icon,
                 'nice_name': nice_name,
                 'category': category,
                 'default_values': default_values}

    # Store function in the register
    if dt_name not in FUNCTIONS_QUEUE:
        FUNCTIONS_QUEUE[dt_name] = {}
    FUNCTIONS_QUEUE[dt_name][signature] = func_dict


def _do_func_registrations():
    for dt_name in FUNCTIONS_QUEUE.keys():
        if dt_name not in FUNCTION_REGISTER.keys():
            FUNCTION_REGISTER[dt_name] = {}
        for signature, func_dict in FUNCTIONS_QUEUE[dt_name].items():
            FUNCTION_REGISTER[dt_name][signature] = func_dict
            Logger.debug('Function registered {0}: {1}'.format(dt_name, signature))
    FUNCTIONS_QUEUE.clear()


def get_functions_map_from_datatype(datatype):
    func_map = FUNCTION_REGISTER.get(datatype['index'])  # type: dict
    return func_map


def get_function_from_signature(signature):
    for dt_func_map in FUNCTION_REGISTER.values():
        if signature in dt_func_map:
            return dt_func_map[signature]
    return None


def get_class_name_from_signature(signature):
    return signature.split('.')[-2]


# ========== PLUGINS =========== #
def load_plugins():
    Logger.info('Loading rig editor plugins...')
    # Clear queues and registers
    NODES_QUEUE.clear()
    FUNCTIONS_QUEUE.clear()
    DATATYPE_REGISTER.clear()
    NODE_REGISTER.clear()
    FUNCTION_REGISTER.clear()

    # Register basic datatypes with register
    DataType._register_basic_types()

    # Load plugins
    success_count = 0
    plugin_files = []
    plugin_paths = []

    for file_name in os.listdir(directories.EDITOR_PLUGINS_PATH):
        if file_name.endswith('.py') and file_name.startswith('node_'):
            plugin_files.append(file_name)
    # Move core files to the front
    plugin_files.insert(0, plugin_files.pop(plugin_files.index('node_function.py')))
    plugin_files.insert(1, plugin_files.pop(plugin_files.index('node_character.py')))
    plugin_paths = [os.path.join(directories.EDITOR_PLUGINS_PATH, file_name)
                    for file_name in plugin_files]

    # Dynamically import plugin files
    for path in plugin_paths:
        p_name = os.path.basename(path).split('.')[0]
        # TODO: Add condition for Python 3 import
        plugin = imp.load_source('luna_builder.rig_nodes.{0}'.format(p_name), path)
        try:
            # Populates datatypes, nodes, function queues
            plugin.register_plugin()
            success_count += 1
        except Exception:
            Logger.exception('Failed to register plugin {0}'.format(p_name))

    # Do actual registrations
    _do_node_registrations()
    _do_func_registrations()

    Logger.info('Successfully loaded {0} plugins'.format(success_count))
