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


@pytest.mark.parametrize('field', (h.UInt8, h.UInt8(), 3))
def test_redefining_fields(field):
    with pytest.raises(NameError):
        class Check(Omri):
            a = field


def test_bytes_length():
    assert len(bytes(Omri())) == 11


def test_non_default_args():
    class Check(h.Struct):
        x = h.UInt8()

        def __init__(self, a):
            super().__init__(a)
            assert a == 3

    c = Check(3)
    c.from_bytes(bytes(c))

    class CheckBad(h.Struct):
        def __init__(self, a):
            super().__init__()

    with pytest.raises(ValueError):
        CheckBad(1)
