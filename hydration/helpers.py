import inspect
from typing import Callable


def as_type(obj):
    return obj if inspect.isclass(obj) else type(obj)


def as_obj(obj):
    return obj if not inspect.isclass(obj) else obj()


def as_stream(data: bytes) -> Callable[[int], bytes]:
    class _StreamReader:
        def __init__(self, _data: bytes):
            self._data = _data

        def read(self, size: int) -> bytes:
            user_data, self._data = self._data[:size], self._data[size:]
            return user_data

    return _StreamReader(data).read


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
