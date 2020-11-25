import pymel.core as pm
from Luna import Config


def switch_geo_picker():
    state = pm.selectType(q=1, p=1)
    pm.selectType(p=not state)


def switch_joint_picker():
    state = pm.selectType(q=1, j=1)
    pm.selectType(j=not state)


def switch_curve_Picker():
    state = pm.selectType(q=1, nc=1)
    pm.selectType(nc=not state)


def switch_xray_joints(state=True, panel=4, *args):
    if state:
        pm.modelEditor("modelPanel{0}".format(panel), e=1, jx=state)
    else:
        currentState = pm.modelEditor("modelPanel{0}".format(panel), q=1, jx=1)
        pm.modelEditor("modelPanel{0}".format(panel), e=1, jx=not currentState)


def isolate_current_panel(add=False, *args):
    panel = pm.paneLayout('viewPanes', q=1, pane1=1)
    state = pm.isolateSelect(panel, q=1, state=1)
    pm.editor(panel, e=1, mainListConnection="activeList")
    pm.isolateSelect(panel, loadSelected=1)
    pm.isolateSelect(panel, state=not state)
    if add:
        pm.editor(panel, e=1, unlockMainConnection=1)
    else:
        pm.editor(panel, e=1, lockMainConnection=1)
