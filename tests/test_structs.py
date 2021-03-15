import pytest
import hydration as h

from .utils import as_reader


class Omri(h.Struct):
    a = h.UInt16(256)
    b = h.UInt8(5)
    c = h.Double(3)


def test_struct_meta_len():
    # noinspection PyTypeChecker
    assert len(Omri()) == len(Omri)


def test_field_copy():
    x = Omri()
    x.a = 3
    y = Omri()
    assert x.a == 3
    assert y.a == 256


@pytest.mark.parametrize('field', (h.UInt8, h.UInt8(), 3))
def test_redefining_fields(field):
    with pytest.raises(NameError):
        # noinspection PyUnusedLocal
        class Check(Omri):
            a = field


def test_bytes_length():
    assert len(bytes(Omri())) == 11


def test_non_default_args():
    class Check(h.Struct):
        x = h.UInt8()

        def __init__(self, a):
            super().__init__(a)
            self.x = a

    c = Check(3)
    assert c.x == 3
    c.from_bytes(bytes(c))

    class CheckBad(h.Struct):
        def __init__(self, a):
            super().__init__()

    with pytest.raises(ValueError):
        CheckBad(1)


class MyStructHeader(h.Struct):
    a = h.UInt8(1)


class MyStructFooter(h.Struct, footer=True):
    d = h.UInt8(4)


class MyStructBody(h.Struct):
    b = h.UInt8(2)
    c = h.UInt8(3)


class MyStruct(MyStructFooter, MyStructHeader, MyStructBody):
    pass


def test_footer():
    assert bytes(MyStruct()) == b'\x01\x02\x03\x04'


def test_from_stream():
    from .utils import MockReader

    class Shustin(h.Struct):
        length = h.UInt16()
        data = h.Vector(length=length, field_type=h.UInt8())

    class NadavLoYazam(h.Struct):
        nadav = h.UInt8()
        lo = h.UInt16()
        yazam = h.UInt32()
        bihlal = h.UInt64()

    shustin = Shustin()
    shustin.length = 32
    shustin.data = [x for x in range(0, 32, 1)]
    my_shustin = Shustin.from_stream(as_reader(bytes(shustin)))
    # assert bytes(shustin) == bytes(my_shustin)
    assert shustin == my_shustin

    nadav = NadavLoYazam()
    nadav.nadav = 3
    nadav.lo = 854
    nadav.yazam = 1512
    nadav.bihlal = 38272
    nadav_lo_yazam = NadavLoYazam.from_stream(as_reader(bytes(nadav)))
    # assert bytes(nadav) == bytes(nadav_lo_yazam)
    assert nadav == nadav_lo_yazam


def test_new_attributes():
    class Becca(h.Struct):
        x = h.UInt8()

    b = Becca()
    with pytest.raises(AttributeError):
        b.y = 3


def test_type_field():
    class Dror(h.Struct):
        a = h.UInt16
        b = h.UInt16()

    d = Dror()
    assert d.a == d.b


def test_inherit_default_args():
    class Amadeus(h.Struct):
        x = h.UInt32

        def __init__(self, x, *args, **kwargs):
            super().__init__(x, *args, **kwargs)

    a = Amadeus(3)
    assert Amadeus(3).from_bytes(bytes(a)) == a
    assert Amadeus(3).from_stream(as_reader(bytes(a))) == a

    class Mozart(Amadeus):
        y = h.UInt16

        def __init__(self, x, y, **kwargs):
            super().__init__(x, y, **kwargs)
            self.y = y

    m = Mozart(4, 5)
    assert Mozart(0, 0).from_bytes(bytes(m)) == m
    assert Mozart(0, 0).from_stream(as_reader(bytes(m))) == m


def test_from_bytes_hooks():
    class Ronen(h.Struct):
        x = h.UInt8(2)
        arr = h.Array(10, h.FieldPlaceholder, value=list(range(10)))

        @h.Struct.from_bytes_hook(arr)
        def foo(self):
            self.arr.type = h.UInt16()

    r = Ronen()
    r.arr.type = h.UInt16()

    r2 = Ronen.from_bytes(bytes(r))
    r3 = Ronen.from_stream(as_reader(bytes(r)))

    assert r2.arr == list(range(10))
    assert r3.arr == list(range(10))
