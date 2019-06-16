import hydration as h


class Isaac(h.Struct):
    arr = h.Array(scalar_type=h.UInt8(3), length=3, value=(1, 2))


def test_vector():
    assert bytes(Isaac()) == b'\x01\x02\x03'


def test_bad_val():
    x = Isaac()
    x.arr = (4,)
    assert bytes(x) == b'\x04\x03\x03'

