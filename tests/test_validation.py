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
    with pytest.raises(ValueError):
        # The validation will raise a ValueError here because the Scalar is the validator, not the struct.
        class BadStruct(h.Struct):
            a = h.UInt8(validator=h.ExactValueValidator(2))


def test_validation_types():
    class Good(h.Struct):
        i32 = h.Int32(5, validator=h.FunctionValidator(lambda z: z > 4))
        i32_range = h.Int32(14, validator=h.RangeValidator(range(0, 30, 2)))
        i32_set = h.Int32(2, validator=h.SetValidator({1, 2, 3}))
        i32_arr = h.Array(length=5, field_type=h.UInt8(5), validator=h.ExactValueValidator(5))

    x = Good()

    with pytest.raises(ValueError):
        x.i32 = 3

    with pytest.raises(ValueError):
        x.i32_range = 15

    with pytest.raises(ValueError):
        x.i32_set = 4

    with pytest.raises(ValueError):
        x.i32_arr = [5, 5, 5, 5, 4]


def test_validation_changes():
    class Rondo(h.Struct):
        paz = h.Int32(5, validator=h.RangeValidator(range(0, 6)))
        omer = h.Array(5, field_type=h.UInt8, validator=h.FunctionValidator(lambda x: 0 <= x <= 30))
        alon = h.UInt8(0, validator=h.RangeValidator(range(0, 125, 1)))
        mishaan = h.Vector(alon, validator=h.ExactValueValidator(0))

    rondo = Rondo()
    rondo.paz = 5
    rondo.omer = [1, 2, 3]
    rondo.mishaan.validator = None
    rondo.mishaan = [0, 1, 2, 3]

    with pytest.raises(ValueError):
        rondo.paz.validator = h.RangeValidator(range(6, 7))

    with pytest.raises(ValueError):
        rondo.omer.validator = h.ExactValueValidator(0)

    with pytest.raises(ValueError):
        rondo.mishaan.validator = h.RangeValidator(range(0, 2, 1))
