import hydration as h


class Garzon(h.Struct):
    arr = h.Array(scalar_type=h.UInt8(3), length=3, value=(1, 2))
    nested_vla_len = h.UInt16()
    nested_vla = h.Vector(h.Int32(), length=nested_vla_len, value=(9, 10, 100))
    x = h.UInt8(5)


class Shine(h.Struct):
    arr = h.Array(scalar_type=h.UInt8(3), length=3, value=(1, 2))
    vec_len = h.UInt8()
    vec = h.Vector(scalar_type=h.UInt8(), length=vec_len)
    y = h.UInt64(9)
    z_len = h.UInt8()
    z = h.Vector(scalar_type=Garzon(), length=z_len, value=[
        Garzon(nested_vla=(11, 12, 13, 14, 15)), Garzon(arr=(9,)), Garzon()])
    vec2_len = h.UInt8()
    vec2 = h.Vector(scalar_type=h.UInt32(), length=vec2_len, value=(53, 99, 123))
    x = h.UInt16(104)


def test_vector():
    x = Shine()
    new_x = x.from_bytes(bytes(x))
    assert x == new_x


def test_vector_len_update():
    x = Shine()
    tmp = (1, 2, 3)
    x.vec = tmp
    assert x.vec_len == len(tmp)
    tmp = (1, 2, 3, 4)
    x.vec = tmp


class Isaac(h.Struct):
    arr = h.Array(scalar_type=h.UInt8(3), length=3, value=(1, 2))
    x = h.UInt8(5)


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
