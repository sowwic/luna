import luna_rig
from luna import Logger
from luna_rig.components import FKIKComponent
from luna_rig.functions import jointFn


class BipedLegComponent(FKIKComponent):

    @classmethod
    def create(cls,
               meta_parent=None,
               hook=0,
               character=None,
               side="c",
               name="leg",
               start_joint=None,
               end_joint=None,
               ik_world_orient=True,
               default_fkik_state=1,
               tag="body"):

        full_input_chain = jointFn.joint_chain(start_joint, end_joint)
        leg_chain = full_input_chain[:3]
        foot_chain = full_input_chain[3:]

        if not len(full_input_chain) == 5:
            Logger.error("{0}: joint chain must be of length 5. Got {1}".format(
                cls.as_str(name_only=True), full_input_chain))
            raise ValueError("Invalid joint chain length.")

        leg_instance = super().create(meta_parent=meta_parent,
                                      hook=hook,
                                      character=character,
                                      side=side,
                                      name=name,
                                      start_joint=leg_chain[0],
                                      end_joint=leg_chain[-1],
                                      ik_world_orient=ik_world_orient,
                                      default_state=default_fkik_state,
                                      param_locator=None,
                                      tag=tag)

        return leg_instance
