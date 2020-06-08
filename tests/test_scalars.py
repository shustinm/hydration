import enum

import pytest

import hydration as h


class Gilad(h.Struct):
    i8 = h.Int8(0)
    i16 = h.Int16(0)
    i32 = h.Int32(0)
    i64 = h.Int64(0)

    u8 = h.UInt8(0)
    u16 = h.UInt16(0)
    u32 = h.UInt32(0)
    u64 = h.UInt64(0)

    flt = h.Float(0)
    dub = h.Double(0)


class Guy(enum.IntEnum):
    a = 1
    b = 2
    c = 3


class Dar(h.Struct):
    d = h.Enum(h.UInt32, Guy)


def test_enums():
    assert Dar().d == Guy.a
    x = Dar()
    x.d = Guy.c
    assert x.from_bytes(bytes(x)).d == Guy.c
    assert x.d.name == 'c'
    assert x.d.value == Guy.c.value

    with pytest.raises(ValueError):
        x.d = 4


def test_different_size():
    g = Gilad()
    assert g.i8 == g.i16


def test_add():
    assert h.UInt8(2) + 3 == 5
    assert 2 + h.UInt8(3) == 5
    assert h.UInt8(2) + h.UInt16(3) == 5


def test_comparisons():
    assert h.UInt16(3) > h.UInt16(2)
    assert h.UInt16(3) == h.UInt16(3)
    assert h.UInt16(4) == h.UInt8(4)
