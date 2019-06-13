import enum
import struct
import abc


class Endianness(enum.Enum):
    Network = '!'
    NativeEndian = '='
    LittleEndian = '<'
    BigEndian = '>'


class Field(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __bytes__(self) -> bytes:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_bytes(cls, data: bytes):
        raise NotImplementedError


class Scalar(Field):
    def __init__(self, value=0, endianness: Endianness = None):
        super().__init__()
        self.value = value
        self.endianness_format = endianness.value if endianness else None
        self.scalar_format = ScalarFormat(self.__class__).name

    def __repr__(self):
        return '{}({})'.format(self.__class__.__qualname__, self.value)

    def __len__(self) -> int:
        return len(bytes(self))

    def __bytes__(self) -> bytes:
        format_string = '{}{}'.format(self.endianness_format or Endianness.NativeEndian.value, self.scalar_format)
        return struct.pack(format_string, self.value)

    @classmethod
    def from_bytes(cls, data: bytes, endianness: Endianness = None):
        endianness = endianness if endianness else Endianness.NativeEndian
        format_string = '{}{}'.format(endianness.value, ScalarFormat(cls).name)
        val = struct.unpack(format_string, data)[0]
        return cls(val, endianness)


class UInt8(Scalar):
    pass


class UInt16(Scalar):
    pass


class UInt32(Scalar):
    pass


class UInt64(Scalar):
    pass


class Int8(Scalar):
    pass


class Int16(Scalar):
    pass


class Int32(Scalar):
    pass


class Int64(Scalar):
    pass


class Float(Scalar):
    pass


class Double(Scalar):
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




