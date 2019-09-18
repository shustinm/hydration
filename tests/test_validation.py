import pytest
import hydration as h


class Tst(h.Struct):
    a = h.UInt8(validator=h.ExactValueValidator(0))


def test_init():
    with pytest.raises(ValueError):
        Tst(a=2)


def test_from_bytes():
    with pytest.raises(ValueError):
        Tst.from_bytes(b'\x02')


def test_bad_struct():
    class BadStruct(h.Struct):
        a = h.UInt8(validator=h.ExactValueValidator(2))

    with pytest.raises(ValueError):
        BadStruct()


def test_validation_types():
    class Good(h.Struct):
        i32 = h.Int32(5, validator=h.FunctionValidator(lambda z: z > 4))
        i32_range = h.Int32(14, validator=h.RangeValidator(range(0, 30, 2)))
        i32_set = h.Int32(2, validator=h.SetValidator({1, 2, 3}))

    x = Good()

    with pytest.raises(ValueError):
        x.i32 = 3

    with pytest.raises(ValueError):
        x.i32_range = 15

    with pytest.raises(ValueError):
        x.i32_set = 4
