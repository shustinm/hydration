import contextlib
import copy
from itertools import chain
from .fields import Field
from collections import OrderedDict, Counter


class StructMeta(type):
    def __new__(mcs, name, bases, attributes):

        # Load all the fields from the parent classes
        base_fields = OrderedDict()
        for base in filter(lambda x: issubclass(x, Struct), bases):
            for field_name in base._field_names:
                base_fields[field_name] = getattr(base, field_name)

        # Check to see if any of the current attributes have already been defined
        for k, v in attributes.items():
            if k in base_fields:
                raise NameError("Field '{}' was defined more than once".format(k))

        # Update the current attributes with the fields from the parents (in order)
        base_fields.update(attributes)
        attributes = base_fields

        # Create the list of the final fields and set the new attributes accordingly
        field_list = []
        for k, v in attributes.items():
            if isinstance(v, Field):
                field_list.append(k)
                attributes[k] = v

        # Also save as attribute so it can be used to iterate over the fields in order
        attributes['_field_names'] = field_list

        return super().__new__(mcs, name, bases, attributes)

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()


class Struct(metaclass=StructMeta):
    @property
    def _fields(self):
        return (object.__getattribute__(self, name) for name in self._field_names)

    def __init__(self):
        super().__init__()
        for name, field in zip(self._field_names, self._fields):
            setattr(self, name, copy.deepcopy(field))

    def __str__(self):
        return '{cls}:\n{data}'.format(cls=self.__class__.__qualname__,
                                       data='\n'.join('\t{}:\t{}'.format(name, field) for name, field in
                                                      zip(self._field_names, self._fields)))

    def __len__(self) -> int:
        return sum(map(len, self._fields))

    def __eq__(self, other) -> bool:
        # noinspection PyProtectedMember
        return all(a == b for a, b in zip(self._fields, other._fields))

    def __bytes__(self) -> bytes:
        return b''.join(map(bytes, self._fields))

    @classmethod
    def from_bytes(cls, data: bytes):
        obj = cls()

        # noinspection PyProtectedMember
        for field_name in obj._field_names:
            field = getattr(obj, field_name)
            split_index = len(field)
            field_data, data = data[:split_index], data[split_index:]
            setattr(obj, field_name, field.from_bytes(field_data).value)

        return obj

    def __getattribute__(self, item):
        fields = super().__getattribute__('_field_names')
        if item in fields:
            return super().__getattribute__(item).value
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self._field_names and not isinstance(value, Field):
            super().__getattribute__(key).value = value
        else:
            super().__setattr__(key, value)
