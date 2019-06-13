from .fields import Field
from collections import OrderedDict


class StructMeta(type):
    def __new__(mcs, name, bases, attributes):
        obj = super().__new__(mcs, name, bases, attributes)
        obj._members = tuple((k, v) for k, v in attributes.items() if isinstance(v, Field))
        return obj

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()


class Struct(metaclass=StructMeta):
    def __str__(self):
        return '{cls}:\n{data}'.format(cls=self.__class__.__qualname__,
                                       data='\n'.join('\t{}:\t{}'.format(k, v) for k, v in self._members))

    def __len__(self) -> int:
        return sum(len(field) for _, field in self._members)

    def __bytes__(self) -> bytes:
        return b''.join(bytes(field) for _, field in self._members)

    @classmethod
    def from_bytes(cls, data: bytes):
        obj = cls()

        # noinspection PyProtectedMember
        for name, field in obj._members:
            split_index = len(field)
            field_data, data = data[:split_index], data[split_index:]
            setattr(obj, name, field.from_bytes(field_data))

        return obj
