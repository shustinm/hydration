import enum
import struct
from .fields import Field


class Endianness(enum.Enum):
    Network = '!'
    NativeEndian = '='
    LittleEndian = '<'
    BigEndian = '>'


class _Scalar(Field):
    @classmethod
    def validate(cls, value):
        try:
            struct.pack(ScalarFormat(cls).name, value)
        except struct.error:
            return False
        return True

    def __init__(self, value, endianness: Endianness):
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

    def __repr__(self):
        return '{}({})'.format(self.__class__.__qualname__, self.value)

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
        self.value = struct.unpack(format_string, data)[0]
        return self


class _IntScalar(_Scalar):
    def __init__(self, value: int = 0, endianness: Endianness = None):
        super().__init__(value, endianness)


class UInt8(_IntScalar):
    pass


class UInt16(_IntScalar):
    pass


class UInt32(_IntScalar):
    pass


class UInt64(_IntScalar):
    pass


class Int8(_IntScalar):
    pass


class Int16(_IntScalar):
    pass


class Int32(_IntScalar):
    pass


class Int64(_IntScalar):
    pass


class _FloatScalar(_Scalar):
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
