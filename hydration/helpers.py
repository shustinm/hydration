import inspect


def as_type(obj):
    return obj if inspect.isclass(obj) else type(obj)


def as_obj(obj):
    return obj if not inspect.isclass(obj) else obj()


def assert_no_property_override(obj, base_class):
    """
    Use this to ensure that a Struct doesn't override properties of Field when using it as one.
    Structs can be used like fields when nesting structs or sequencing them.
    :raises: NameError if a property was overridden.
    """
    for attr_name in dir(obj):
        if hasattr(base_class, attr_name):
            if (isinstance(getattr(base_class, attr_name), property) and
                    not isinstance(getattr(type(obj), attr_name), property)):
                raise NameError(f"'{attr_name}' is an invalid name for an attribute in a sequenced or nested struct")
