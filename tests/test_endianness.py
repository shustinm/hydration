import hydration as h
from enum import IntEnum


class Lia(IntEnum):
    A = 1
    B = 2


class Tal(h.Struct):
    x = h.UInt64(endianness=h.BigEndian)
    z = h.UInt64
    t = h.UInt8
    u = h.Enum(h.UInt16, Lia)


class Hod(Tal, endianness=h.LittleEndian):
    y = h.UInt32()


class Yuval(Tal, endianness=h.BigEndian):
    pass


def test_endianness_override():
    assert Tal().x.endianness_format == h.BigEndian.value
    assert Hod().x.endianness_format == h.BigEndian.value
    assert Hod().y.endianness_format == h.LittleEndian.value
    assert Hod().z.endianness_format == h.LittleEndian.value
    assert Hod().u.type.endianness_format == h.LittleEndian.value


def test_uint8_endianness():
    class A(h.Struct, endianness=h.BigEndian):
        t = h.UInt8

    class B(h.Struct):
        t = h.UInt8

    assert A() == B()
    assert bytes(A()) == bytes(B())


def test_enum_endianness():
    assert Tal.u.type.endianness_format == h.Endianness.Default.value
    assert Yuval.u.type.endianness_format == h.Endianness.BigEndian.value
    assert bytes(h.Enum(h.UInt16, Lia, Lia.A)) == bytes(h.UInt16(1))
    assert bytes(h.Enum(h.UInt16(endianness=h.BigEndian), Lia, Lia.A)) == bytes(h.UInt16(1, endianness=h.BigEndian))
    assert Yuval().u.type.endianness_format == h.BigEndian.value
    assert bytes(Yuval(u=1))[-2:] == bytes(h.UInt16(1, endianness=h.BigEndian))
