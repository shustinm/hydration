import pytest

import hydration as h


class Garzon(h.Struct):
    arr = h.Array(field_type=h.UInt8(3), length=3, value=(1, 2), fill=True)
    nested_vla_len = h.UInt16()
    nested_vla = h.Vector(field_type=h.Int32(), length=nested_vla_len, value=(9, 10, 100))
    x = h.UInt8(5)


class Shine(h.Struct):
    arr = h.Array(field_type=h.UInt8(3), length=3, value=(1, 2), fill=True)
    vec_len = h.UInt8()
    vec = h.Vector(field_type=h.UInt8(), length=vec_len)
    y = h.UInt64(9)
    z_len = h.UInt8()
    z = h.Vector(field_type=Garzon(), length=z_len, value=[
        Garzon(nested_vla=(11, 12, 13, 14, 15)), Garzon(arr=(9,)), Garzon()])
    vec2_len = h.UInt8()
    vec2 = h.Vector(field_type=h.UInt32(), length=vec2_len, value=(53, 99, 123))
    x = h.UInt16(104)


def test_vector():
    x = Shine()
    new_x = Shine.from_bytes(bytes(x))
    assert x == new_x


def test_vector_len_update():
    x = Shine()
    tmp = (1, 2, 3)
    x.vec = tmp
    assert x.vec_len == len(tmp)
    tmp = (1, 2, 3, 4)
    x.vec = tmp


class Isaac(h.Struct):
    arr = h.Array(field_type=h.UInt8(3), length=3, value=(1, 2), fill=True)
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
        arr = h.Array(3, h.UInt8(8), validator=lambda x: x > 7, fill=True)

    Shustin()

    class Shustin2(h.Struct):
        arr = h.Array(3, h.UInt8(8), validator=lambda x: x > 9, fill=True)

    with pytest.raises(ValueError):
        Shustin2()


def test_ipv4():
    class Venice(h.Struct):
        ip = h.IPv4()

    assert str(Venice().ip) == '0.0.0.0'
    assert Venice.from_bytes(bytes(Venice(ip='127.0.0.1'))) == Venice(ip='127.0.0.1')

    with pytest.raises(ValueError):
        Venice.from_bytes(bytes(Venice(ip='127.0.0.1'))[:-1])


def test_type_field():
    class Lior(h.Struct):
        a = h.Array(5, h.UInt16, fill=True)

    class Raif(h.Struct):
        a = h.Array(5, h.UInt16(), fill=True)

    assert Lior().a == Raif().a
    assert Lior.a == Raif.a

    class Raif(h.Struct):
        a = h.Array(5, h.UInt16(1))

    assert Lior().a != Raif().a
    assert Lior.a != Raif.a


def test_seq_as_list():
    s = Shine()
    assert set(s.arr) == {1, 2, 3}
    assert list(s.arr) == [1, 2, 3]

    with pytest.raises(ValueError):
        s.arr.append(2)

    assert s.arr + [4, 5] == [1, 2, 3, 4, 5]
    assert [4, 5] + s.arr == [4, 5, 1, 2, 3]


class Yakov(h.Struct):
    arr = h.Array(3)


def test_seq_no_fill_as_list():
    y = Yakov()
    assert y.arr == []

    y.arr.append(3)
    assert y.arr == [3]

    y.arr.extend([4, 5])
    assert y.arr == [3, 4, 5]

    with pytest.raises(ValueError):
        y.arr.append(1)

    with pytest.raises(ValueError):
        y.arr.extend([1])


def test_array_deserialization():
    class Data(h.Struct):
        data = h.Array(10)

    d = Data(data=[3] * 10)
    b = bytes(d)
    assert Data.from_bytes(b).data == d.data
