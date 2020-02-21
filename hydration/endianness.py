import enum


class Endianness(enum.Enum):
    Default = ''
    Network = '!'
    NativeEndian = '='
    LittleEndian = '<'
    BigEndian = '>'
