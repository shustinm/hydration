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

