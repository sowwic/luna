import inspect


def get_classes(module_object, as_dict=False):
    cls_members = inspect.getmembers(module_object, inspect.isclass)
    if as_dict:
        cls_dict = {}
        for member in cls_members:
            cls_dict[member[0]] = member[1]
        return cls_dict
    return cls_members


def get_methods(class_object, private=False):
    methods = inspect.getmembers(class_object, inspect.ismethod)
    if not private:
        methods = [pair for pair in methods if not pair[0].startswith("_")]
    return methods
