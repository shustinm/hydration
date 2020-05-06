import pytest
import hydration as h


class Time(h.Struct):
    time = h.UInt64(3)


class Log(h.Struct):
    data = h.UInt8(2)
    time = Time()


class Ron(h.Struct):
    a = h.UInt64(55)
    log = Log()
    b = h.UInt64(56)


def test_nested():
    a = Ron()
    assert a.from_bytes(bytes(a)) == a


class Card(h.Struct):
    value = h.UInt8()
    suit = h.UInt8()


def test_property_override_sequence():
    with pytest.raises(NameError):
        # noinspection PyUnusedLocal
        class Hand(h.Struct):
            cards = h.Array(5, Card)


def test_property_override_nested_struct():
    with pytest.raises(NameError):
        # noinspection PyUnusedLocal
        class Hand(h.Struct):
            card1 = Card()
