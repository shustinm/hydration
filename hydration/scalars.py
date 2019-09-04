import enum
import struct
from enum import IntEnum
from typing import Union, Callable, Type, Optional

from .fields import Field

scalar_values = Union[int, float]


class Endianness(enum.Enum):
    Network = '!'
    NativeEndian = '='
    LittleEndian = '<'
    BigEndian = '>'


class Scalar(Field):

    def __init__(self, value: scalar_values, endianness: Endianness, validator: Callable = None):
        super().__init__()
        self.validator = validator
        self.endianness_format = endianness.value if endianness else ''
        self.scalar_format = ScalarFormat(self.__class__).name
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.validate(value):
            self._value = value
        else:
            raise ValueError('Value {} is invalid for field type {}'.format(value, self.__class__.__qualname__))

    def validate(self, value):
        try:
            struct.pack(self.scalar_format, value)

            if self.validator:
                return self.validator(value)

        except struct.error:
            return False
        return True

    def __repr__(self):
        return '{}({})'.format(self.__class__.__qualname__, self.value)

    def __str__(self):
        return repr(self)

    def __len__(self) -> int:
        return len(bytes(self))

    def __bytes__(self) -> bytes:
        format_string = '{}{}'.format(self.endianness_format,
                                      self.scalar_format)
        return struct.pack(format_string, self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def from_bytes(self, data: bytes):
        format_string = '{}{}'.format(self.endianness_format, ScalarFormat(self.__class__).name)
        # noinspection PyAttributeOutsideInit
        self.value = struct.unpack(format_string, data)[0]
        return self


class _IntScalar(Scalar):
    def __init__(self, value: int = 0, endianness: Endianness = None, validator: Callable = None):
        super().__init__(value, endianness, validator)


class UInt8(_IntScalar):
    # Override constructor because this scalar doesn't have endianness
    def __init__(self, value: int = 0, validator: Callable = None):
        super().__init__(value, validator=validator)


class UInt16(_IntScalar):
    pass


class UInt32(_IntScalar):
    pass


class UInt64(_IntScalar):
    pass


class Int8(_IntScalar):
    # Override constructor because this scalar doesn't have endianness
    def __init__(self, value: int = 0, validator: Callable = None):
        super().__init__(value, validator=validator)


class Int16(_IntScalar):
    pass


class Int32(_IntScalar):
    pass


class Int64(_IntScalar):
    pass


class _FloatScalar(Scalar):
    def __init__(self, value: float = 0.0, endianness: Endianness = None, validator: Callable = None):
        super().__init__(float(value), endianness, validator)


class Float(_FloatScalar):
    pass


class Double(_FloatScalar):
    pass


class ScalarFormat(enum.Enum):
    B = UInt8
    H = UInt16
    I = UInt32
    Q = UInt64
    b = Int8
    h = Int16
    i = Int32
    q = Int64
    f = Float
    d = Double


class Enum(Field):
    def __init__(self, scalar_type: _IntScalar, enum_class: Type[enum.IntEnum], value: Optional[enum.IntEnum] = None):
        if scalar_type.value != 0:
            raise ValueError('Do not set a value in the given scalar type: {}'.format(scalar_type))
        self.type = scalar_type
        self.enum_class = enum_class
        # noinspection PyTypeChecker
        self.value = value or next(iter(self.enum_class))
        self.type.value = self.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: IntEnum):
        if not self.validate(value):
            raise ValueError('Given value {} is invalid for {} or for {}'.format(value, self.enum_class, self.type))
        self.type.value = value
        self._value = value

    def __repr__(self) -> str:
        return '{}({}, {}, {})'.format(self.__class__.__qualname__,
                                       self.type,
                                       self.enum_class,
                                       self.value)

    def __str__(self) -> str:
        return '{}({})'.format(self.type.__class__.__qualname__, repr(self.value))

    def __len__(self) -> int:
        return len(self.type)

    def __bytes__(self) -> bytes:
        return bytes(self.type)

    def from_bytes(self, data: bytes):
        self.type.from_bytes(data)
        self.value = self.type.value
        return self

    def validate(self, value):
        try:
            self.enum_class(value)
        except ValueError:
            return False
        return self.type.validate(value)
