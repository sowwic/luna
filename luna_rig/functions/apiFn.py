from PySide2 import QtWidgets
import pymel.api as pma


def get_MObject(name):
    name = str(name)
    sel = pma.MSelectionList()
    sel.add(name)
    mobj = pma.MObject()
    sel.getDependNode(0, mobj)
    return mobj


def get_MDagPath_and_components(components):
    sel_list = pma.MSelectionList()
    for each in components:
        sel_list.add(each)
    dag = pma.MDagPath()
    mobj = pma.MObject()
    sel_list.getDagPath(0, dag, mobj)
    return dag, mobj


def get_dag_path(node):
    sel = pma.MSelectionList()
    sel.add(str(node))
    dag_path = pma.MDagPath()
    sel.getDagPath(0, dag_path)
    return dag_path


def get_all_dgnodes(in_node, direction, mfn_type):
    nodes = []
    # Create selection list
    sel = pma.MSelectionList()
    sel.add(in_node)
    mobj = pma.MObject()
    sel.getDependNode(0, mobj)
    # Create dg iterator
    iter_dg = pma.MItDependencyGraph(mobj, direction, pma.MItDependencyGraph.kPlugLevel)
    while not iter_dg.isDone():
        current_item = iter_dg.currentItem()
        depend_node_fn = pma.MFnDependencyNode(current_item)
        if current_item.hasFn(mfn_type):
            name = depend_node_fn.name()
            nodes.append(name)
        iter_dg.next()

    return nodes
