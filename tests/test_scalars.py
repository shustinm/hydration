import hydration as h
import pytest


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


def test_field_types():
    x = Gilad()
    assert type(x.i8) == int
    assert type(x.i16) == int
    assert type(x.i32) == int
    assert type(x.i64) == int
    assert type(x.u8) == int
    assert type(x.u16) == int
    assert type(x.u32) == int
    assert type(x.u64) == int
    assert type(x.flt) == float
    assert type(x.dub) == float


def test_validation():
    class Good(h.Struct):
        i32 = h.Int32(5, validator=lambda z: z > 4)
        i32_range = h.Int32(14, validator=lambda z: z in range(0, 30, 2))
        i32_set = h.Int32(2, validator=lambda z: z in {1, 2, 3})

    x = Good()

    with pytest.raises(ValueError):
        x.i32 = 3

    with pytest.raises(ValueError):
        x.i32_range = 15

    with pytest.raises(ValueError):
        x.i32_set = 4

    with pytest.raises(ValueError):
        class Bad(h.Struct):
            i32 = h.Int32(5, validator=lambda y: y > 5)
            i32_range = h.Int32(15, validator=lambda y: y in range(0, 30, 2))
            i32_set = h.Int32(0, validator=lambda y: y in {1, 2, 3})
