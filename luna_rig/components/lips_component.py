import pymel.core as pm
from luna import Logger
import luna_rig
import luna_rig.functions.curveFn as curveFn
import luna_rig.functions.rivetFn as rivetFn
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.nameFn as nameFn


class RibbonLipsComponent(luna_rig.AnimComponent):

    @classmethod
    def create(cls,
               meta_parent=None,
               side='c',
               name='lips',
               hook=0,
               character=None,
               tag='face'):
        instance = super(RibbonLipsComponent, cls).create(meta_parent=meta_parent, side=side, name=name, hook=hook, character=character, tag=tag)  # type: RibbonLipsComponent

        return instance
