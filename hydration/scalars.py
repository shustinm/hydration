import enum
import struct
from typing import Union

from .fields import Field


scalar_values = Union[int, float]


class Endianness(enum.Enum):
    Network = '!'
    NativeEndian = '='
    LittleEndian = '<'
    BigEndian = '>'


class Scalar(Field):
    def __init__(self, value: scalar_values, endianness: Endianness):
        super().__init__()
        self._value = value
        self.endianness_format = endianness.value if endianness else ''
        self.scalar_format = ScalarFormat(self.__class__).name

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
    def __init__(self, value: int = 0, endianness: Endianness = None):
        super().__init__(value, endianness)


class UInt8(_IntScalar):
    # Override constructor because this scalar doesn't have endianness
    def __init__(self, value: int = 0):
        super().__init__(value)


class UInt16(_IntScalar):
    pass


class UInt32(_IntScalar):
    pass


class UInt64(_IntScalar):
    pass


class Int8(_IntScalar):
    # Override constructor because this scalar doesn't have endianness
    def __init__(self, value: int = 0):
        super().__init__(value)


class Int16(_IntScalar):
    pass


class Int32(_IntScalar):
    pass


class Int64(_IntScalar):
    pass


class _FloatScalar(Scalar):
    def __init__(self, value: float = 0.0, endianness: Endianness = None):
        super().__init__(float(value), endianness)


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
