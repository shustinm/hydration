import copy
from abc import ABC
from collections import UserList
from typing import Sequence, Optional, Any, Union, Iterable
from itertools import islice, chain

from .base import Struct
from .helpers import as_obj, assert_no_property_override
from .message import FieldType
from .fields import Field, VLA
from .scalars import _IntScalar, UInt8
from .validators import SequenceValidator, as_validator, ValidatorType, ValidatorABC


class _Sequence(UserList, Field, ABC):
    def __init__(self, field_type: FieldType, value: Sequence[Any] = (), validator: Optional[ValidatorType] = None):
        super().__init__()
        self.type = as_obj(field_type)
        assert_no_property_override(self.type, _Sequence)
        self.validator = as_validator(validator)
        self.value = value

    @property
    def validator(self) -> ValidatorABC:
        return self._validator

    @validator.setter
    def validator(self, value: ValidatorABC):
        self._validator = SequenceValidator(value)

    @property
    def value(self):
        return self.data

    @value.setter
    def value(self, value):
        self.data = value

    def __bytes__(self) -> bytes:
        if len(self.value) != len(self):
            raise ValueError(f'Array value ({self.value}) does not match the provided length ({len(self)}). '
                             f'Consider passing `fill=True` to the {self.__class__.__name__} constructor')

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
        return '{}{}'.format(self.__class__.__qualname__, self.value)

    def __repr__(self) -> str:
        return '{}(field_type={}, length={}, value={})'.format(
            self.__class__.__qualname__, self.type, len(self), self.value)

    def __add__(self, other):
        return self.data + list(other)

    def __radd__(self, other):
        return list(other) + self.data

    def __iadd__(self, other):
        self.value = self.data + list(other)
        return self

    @property
    def size(self):
        ret_val = 0
        # The sequences are homogeneous, but the size of each item isn't always the same
        # So we must loop through all items, and sum their size.
        for val in self.value:
            if isinstance(val, (Field, Struct)):
                ret_val += val.size
            else:
                ret_val += self.type.size

        return ret_val

    def __getitem__(self, item):
        return self.data[item]

    def append(self, item) -> None:
        self.value = self.data + [item]

    def insert(self, key: int, item) -> None:
        self.data.insert(key, item)
        self.value = self.data

    def pop(self, i: int = ...):
        self.data.pop(i)
        self.value = self.data

    def remove(self, item) -> None:
        self.data.remove(item)
        self.value = self.data

    def clear(self) -> None:
        self.value = []

    def extend(self, other: Iterable) -> None:
        self.data.extend(other)
        self.value = self.data


class Array(_Sequence):
    def __init__(self, length: int,
                 field_type: FieldType = UInt8,
                 value: Optional[Sequence[Any]] = (),
                 validator: Optional[ValidatorType] = None,
                 fill: bool = False):
        self.length = length
        self.fill = fill
        super().__init__(field_type=field_type, value=value, validator=validator)

    def assert_value_not_too_long(self, value):
        """Make sure that the given value isn't too long"""
        if len(value) > len(self):
            raise ValueError('Length will be too long. Data length was {}. Max is {} but tried to add {}'.format(
                len(self.data), len(self), len(value)
            ))

    def fill_if_necessary(self):
        """
        Extend with the value of the default field value to fill the length (this tuple might be empty).
        Will only fill if `self.fill` is `True`
        """
        if self.fill:
            self.data.extend(self.type.value for _ in range(len(self) - len(self.data)))

    @_Sequence.value.setter
    def value(self, value: Sequence[Any]):
        self.assert_value_not_too_long(value)
        self.data = list(value)
        self.fill_if_necessary()

    def __len__(self) -> int:
        return self.length

    def __delitem__(self, key) -> None:
        super().__delitem__(key)
        self.fill_if_necessary()

    @property
    def size(self):
        return len(self) * len(self.type)


class Vector(_Sequence, VLA):

    def __init__(self, length: Union[_IntScalar, str],
                 field_type: FieldType = UInt8,
                 value: Optional[Sequence[Any]] = (),
                 validator: Optional[ValidatorType] = None):
        VLA.__init__(self, length)
        _Sequence.__init__(self, field_type=field_type, value=(), validator=validator)
        self.value = value

    # noinspection PyAttributeOutsideInit
    @_Sequence.value.setter
    def value(self, value):
        self.data = list(value)

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


class IPv4(Array):
    def __init__(self, value: str = '0.0.0.0'):
        super().__init__(field_type=UInt8(), length=4, value=value)

    @_Sequence.value.setter
    def value(self, value: str):
        x = value.split('.')
        if len(x) != 4:
            raise ValueError('IP length mismatch. Expected 4, got {}'.format(len(x)))
        self.data = list(int(z) for z in x)

    def __str__(self):
        return '.'.join(str(x) for x in self.value)


def byte_chunks(x: bytes, chunk_size: int):
    x = iter(x)
    return iter(lambda: bytes(islice(x, chunk_size)), b'')
