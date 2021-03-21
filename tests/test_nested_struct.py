import pytest
import hydration as h

from .utils import as_reader


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
    assert a.from_stream(as_reader(bytes(a))) == a


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


def test_entanglement():
    l1 = Log()
    l2 = Log()

    assert l1.time is not l2.time

    l1.time.time = 4
    assert l2.time.time == 3
