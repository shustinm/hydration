import inspect


def as_type(obj):
    return obj if inspect.isclass(obj) else type(obj)


def as_obj(obj):
    return obj if not inspect.isclass(obj) else obj()
