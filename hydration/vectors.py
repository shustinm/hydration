import copy
from abc import ABC
from typing import Sequence, Optional, Union, Any, Type
from itertools import islice, chain

from hydration.helpers import as_type, as_obj
from . import Struct
from .fields import Field, VLA
from .scalars import _IntScalar, UInt8
from .validators import Validator, SequenceValidator


class _Sequence(Field, ABC):
    def __init__(self, field_type: Union[Field, Struct, Type[Field], Type[Struct]],
                 value: Sequence[Any] = (),
                 validator: Optional[Validator] = None):
        self.type = as_obj(field_type)
        self.validator = validator
        self.value = value

    @property
    def validator(self) -> Validator:
        return self._validator

    @validator.setter
    def validator(self, value: Validator):
        self._validator = SequenceValidator(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
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
        return '{}{}'.format(self.__class__.__qualname__, self.value)

    def __repr__(self) -> str:
        return '{}(field_type={}, length={}, value={})'.format(
            self.__class__.__qualname__, self.type, len(self), self.value)

    def __eq__(self, other):
        return self.type == other.type and all(x == y for x, y in zip(self.value, other.value))

    def __ne__(self, other):
        return not self == other


class Array(_Sequence):
    def __init__(self, length: int,
                 field_type: Union[Field, Struct, Type[Field], Type[Struct]] = UInt8,
                 value: Optional[Sequence[Any]] = (),
                 validator: Optional[Validator] = None):
        self.length = length
        super().__init__(field_type=field_type, value=value, validator=validator)

    # noinspection PyAttributeOutsideInit
    @_Sequence.value.setter
    def value(self, value: Sequence[Any]):
        # Make sure that the given value isn't too long
        if len(value) > len(self):
            raise ValueError('Given value is too long for the length given. Expected {} or less, given {}'.format(
                len(self), len(value)
            ))

        # Extend with the value of the default field value to fill the length (this tuple might be empty)
        extension = (self.type.value,) * (len(self) - len(value))

        self._value = tuple(chain(value, extension))

    def __len__(self) -> int:
        return self.length


class Vector(_Sequence, VLA):

    def __init__(self, length: _IntScalar,
                 field_type: Union[Field, Struct, Type[Field], Type[Struct]] = UInt8,
                 value: Optional[Sequence[Any]] = (),
                 validator: Optional[Validator] = None):
        VLA.__init__(self, length)
        _Sequence.__init__(self, field_type=field_type, value=(), validator=validator)
        self.value = value

    # noinspection PyAttributeOutsideInit
    @_Sequence.value.setter
    def value(self, value):
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


class IPv4(Array):
    def __init__(self, value: str = '0.0.0.0'):
        super().__init__(field_type=UInt8(), length=4, value=value)

    @_Sequence.value.setter
    def value(self, value: str):
        x = value.split('.')
        if len(x) != 4:
            raise ValueError('IP length mismatch. Expected 4, got {}'.format(len(x)))
        self._value = tuple(int(z) for z in x)

    def __str__(self):
        return '.'.join(str(self.value))


def byte_chunks(x: bytes, chunk_size: int):
    x = iter(x)
    return iter(lambda: bytes(islice(x, chunk_size)), b'')
