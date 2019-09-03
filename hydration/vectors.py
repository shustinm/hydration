import copy
from abc import ABC
from typing import Sequence, Optional, Union
from itertools import islice, chain

from hydration import Struct
from hydration.fields import Field, VLA
from hydration.scalars import scalar_values, _IntScalar


class _Sequence(Field, ABC):
    def __init__(self, scalar_type: Union[Field, Struct], value: Sequence[scalar_values] = ()):
        self.type = scalar_type
        self._value = value

    def __bytes__(self) -> bytes:
        field_type = copy.deepcopy(self.type)

        result = bytearray()
        for val in self.value:
            field_type.value = val
            result.extend(bytes(field_type))

        return bytes(result)

    def from_bytes(self, data: bytes):
        field_type = copy.deepcopy(self.type)
        self.value = tuple(field_type.from_bytes(chunk).value for chunk in byte_chunks(data, len(field_type)))
        return self

    def __str__(self):
        return '{}{}'.format(self.type.__class__.__qualname__, self.value)

    def __eq__(self, other):
        return self.type == other.type and all (x == y for x, y in zip(self.value, other.value))

    def __ne__(self, other):
        return not self == other

    def validate(self, value):
        return all(self.type.validate(val) for val in value)


class Array(_Sequence):
    def __init__(self, scalar_type: Union[Field, Struct], length: int, value: Optional[Sequence[scalar_values]] = ()):
        super().__init__(scalar_type)
        self.length = length
        self.value = tuple(value)

    def __repr__(self) -> str:
        return '{}(scalar_type={}, length={}, value={})'.format(
            self.__class__.__qualname__, self.type, self.length, self.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: Sequence[scalar_values]):
        # Make sure that the given value isn't too long
        if len(value) > self.length:
            raise ValueError('Given value is too long for the length given. Expected {} or less, given {}'.format(
                self.length, len(value)
            ))

        # Validate the given value
        if not self.validate(value):
            raise ValueError('Value {} is invalid for field type {}'.format(value, self.__class__.__qualname__))

        # Extend with the value of the default scalar value (extend might be empty)
        extend = tuple(self.type.value for _ in range(self.length - len(value)))

        self._value = tuple(chain(value, extend))

    def __len__(self) -> int:
        return self.length * len(self.type)


class Vector(_Sequence, VLA):

    def __init__(self, scalar_type: Union[Field, Struct], length: _IntScalar, value: Optional[Sequence] = ()):
        VLA.__init__(self, length)
        _Sequence.__init__(self, scalar_type, ())
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # Validate the given value
        if not self.validate(value):
            raise ValueError('Value {} is invalid for field type {}'.format(value, self.__class__.__qualname__))

        # Convert value to a mutable list and set
        self._value = value

        # This assumes that the Struct will update the length field's value
        self.length = len(value)

    def from_bytes(self, data: bytes):
        if isinstance(self.type, Field):
            return super().from_bytes(data[:len(self) * len(self.type)])
        else:
            val = []
            for _ in range(len(self)):
                next_obj = self.type.from_bytes(data)
                val.append(next_obj)
                data = data[len(bytes(next_obj)):]
            self.value = val
            return self

    def __len__(self) -> int:
        return VLA.__len__(self)

    def __repr__(self) -> str:
        return str(self)


def byte_chunks(x: bytes, chunk_size: int):
    x = iter(x)
    return iter(lambda: bytes(islice(x, chunk_size)), b'')
