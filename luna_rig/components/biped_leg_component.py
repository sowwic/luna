import luna_rig
from luna_rig.components import FKIKComponent


class BipedLegComponent(FKIKComponent):

    @classmethod
    def create(cls, meta_parent=None,
               hook=0,
               character=None,
               side="c", name="leg",
               start_joint=None,
               end_joint=None,
               ik_world_orient=False,
               default_state=1,
               tag="body"):
        leg_instance = super().create(meta_parent=meta_parent,
                                      hook=hook,
                                      character=character,
                                      side=side,
                                      name=name,
                                      start_joint=start_joint,
                                      end_joint=end_joint,
                                      ik_world_orient=ik_world_orient,
                                      default_state=default_state,
                                      param_locator=None,
                                      tag=tag)

        return leg_instance
