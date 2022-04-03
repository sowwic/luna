import uuid


class Serializable(object):

    @classmethod
    def as_str(cls, name_only=False):
        """Get a string representation of class path.

        :return: Class string e.g luna_rig.components.fk_component.FKComponent
        :rtype: str
        """
        module_name = cls.__module__
        cls_name = cls.__name__
        if name_only:
            return cls_name
        meta_type_str = ".".join([module_name, cls_name])
        return meta_type_str

    def __init__(self):
        self.uid = str(uuid.uuid4())

    def serialize(self):
        raise NotImplementedError()

    def deserialize(self, data, hashmap=None):
        raise NotImplementedError()
