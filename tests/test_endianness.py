import hydration as h


class Tal(h.Struct):
    x = h.UInt64(endianness=h.BigEndian)
    z = h.UInt64
    t = h.UInt8


class Hod(Tal, endianness=h.LittleEndian):
    y = h.UInt32()


def test_endianness_override():
    assert Tal().x.endianness_format == h.BigEndian.value
    assert Hod().x.endianness_format == h.BigEndian.value
    assert Hod().y.endianness_format == h.LittleEndian.value
    assert Hod().z.endianness_format == h.LittleEndian.value


def test_uint8_endianness():
    class A(h.Struct, endianness=h.BigEndian):
        t = h.UInt8

    class B(h.Struct):
        t = h.UInt8

    assert A() == B()
    assert bytes(A()) == bytes(B())
