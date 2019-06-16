import copy
from abc import ABC
from typing import Sequence

from .fields import Field
from hydration.scalars import Scalar, scalar_values


class _Vector(Field, ABC):
    def __init__(self, scalar_type: Scalar, value: Sequence[scalar_values]):
        self.type = scalar_type
        self._value = value


class Array(_Vector):
    def __init__(self, scalar_type: Scalar, length: int, value: Sequence[scalar_values] = ()):
        super().__init__(scalar_type, value)
        self.length = length
        self.value = value

    def __repr__(self) -> str:
        return '{}(scalar_type={}, length={}, value={})'.format(
            self.__class__.__qualname__, self.type, self.length, self.value)

    def __str__(self):
        return '{}{}'.format(self.type.__class__.__qualname__, self.value)

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

        # Convert value to a mutable list
        arr = list(value)

        # If the length of the given value isn't enough to fill length
        if len(arr) < self.length:
            # Extend it with the value of the given scalar
            arr.extend(self.type.value for _ in range(self.length - len(arr)))

        self._value = arr

    def __len__(self) -> int:
        return self.length * len(self.type)

    def __bytes__(self) -> bytes:
        field_type = copy.deepcopy(self.type)

        result = bytearray()
        for val in self.value:
            field_type.value = val
            result.extend(bytes(field_type))

        return bytes(result)

    @classmethod
    def from_bytes(cls, data: bytes):
        pass

    def validate(self, value):
        return all(self.type.validate(val) for val in value)
