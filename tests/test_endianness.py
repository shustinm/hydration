import pytest
import hydration as h


@pytest.fixture(autouse=True)
def revert_default_endianness():
    yield
    h.Settings.DefaultEndianness = h.Endianness.Default


class Tal(h.Struct):
    x = h.UInt64(endianness=h.Endianness.Network)


class Hod(h.Struct, endianness=h.Endianness.NativeEndian):
    y = h.UInt32()


def test_endianness_override():
    assert Tal().x.endianness_format == h.Endianness.Network.value
    assert Hod().y.endianness_format == h.Endianness.NativeEndian.value


def test_global_endianness():
    var = h.UInt64()
    assert var.endianness_format != h.Endianness.BigEndian.value
    h.Settings.DefaultEndianness = h.Endianness.BigEndian
    assert var.endianness_format == h.Endianness.BigEndian.value
    var2 = h.UInt32()
    assert var2.endianness_format == var.endianness_format == h.Endianness.BigEndian.value

    h.Settings.DefaultEndianness = h.Endianness.LittleEndian
    assert var2.endianness_format == var.endianness_format == h.Endianness.LittleEndian.value
