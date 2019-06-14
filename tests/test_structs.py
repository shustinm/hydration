import pytest
import hydration as h


class Omri(h.Struct):
    a = h.UInt16(256)
    b = h.UInt8(5)
    c = h.Double(3)


def test_field_copy():
    x = Omri()
    x.a = 3
    y = Omri()
    assert x.a == 3
    assert y.a == 256


def test_field_types():
    x = Omri()
    assert type(x.a) == int
    assert type(x.b) == int
    assert type(x.c) == float


@pytest.mark.parametrize('field', (h.UInt8, h.UInt8(), 3))
def test_redefining_fields(field):
    with pytest.raises(NameError):
        class Check(Omri):
            a = field


def test_bytes_length():
    assert len(bytes(Omri())) == 11
