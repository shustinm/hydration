import pytest
import hydration as h


class Tst(h.Struct):
    a = h.UInt8(validator=0)


def test_init():
    with pytest.raises(ValueError):
        Tst(a=2)


def test_from_bytes():
    with pytest.raises(ValueError):
        Tst.from_bytes(b'\x02')


def test_bad_struct():
    with pytest.raises(ValueError):
        # noinspection PyUnusedLocal
        class BadStruct(h.Struct):
            a = h.UInt8(validator=2)


def test_validation_types():
    class Good(h.Struct):
        i32 = h.Int32(5, validator=lambda z: z > 4)
        i32_range = h.Int32(14, validator=range(0, 30, 2))
        i32_set = h.Int32(2, validator={1, 2, 3})
        i32_arr = h.Array(length=5, field_type=h.UInt8(5), validator=5)

    x = Good()

    with pytest.raises(ValueError):
        x.i32 = 3

    with pytest.raises(ValueError):
        x.i32_range = 15

    with pytest.raises(ValueError):
        x.i32_set = 4

    with pytest.raises(ValueError):
        x.i32_arr = [5, 5, 5, 5, 4]
