import hydration as h


class Isaac(h.Struct):
    arr = h.Array(scalar_type=h.UInt8(3), length=3, value=(1, 2))
    x = h.UInt8(5)


class Shine(h.Struct):
    arr = h.Array(scalar_type=h.UInt8(3), length=3, value=(1, 2))
    vec_len = h.UInt8()
    vec = h.Vector(scalar_type=h.UInt8(), length=vec_len)


def test_vector():
    x = Shine()
    tmp = (1, 2, 3)
    x.vec = tmp
    assert x.vec_len == len(tmp)
    tmp = (1, 2, 3, 4)
    x.vec = tmp
    assert x.vec_len == len(tmp)


def test_bad_val():
    x = Isaac()
    x.arr = (4,)
    assert bytes(x) == b'\x04\x03\x03\x05'


def test_array():
    x = Isaac()
    assert x == Isaac.from_bytes(bytes(x))
    assert bytes(x) == b'\x01\x02\x03\x05'


def test_good_validator():
    class Shustin(h.Struct):
        # arr = h.Array(scalar_type=h.UInt8(8), length=3, validator=lambda items: all(item > 7 for item in items))
        pass
