import hydration as h


class Tomer(h.Struct):
    b = h.UInt8(5)
    c = h.Double(3)
    body_len = h.InclusiveLengthField(h.UInt16())


class Lior(h.Struct):
    a = h.Array(5)


def test_message():
    x = Tomer() / Lior() / Tomer()
    assert x[0] == x[Tomer] == x[(Tomer, 0)]
    assert x[-1] == x[(Tomer, 1)]
    assert len(x) == len(bytes(x))
    assert x[Tomer].body_len == len(Tomer()) * 2 + len(Lior())


def test_bytes_suffix():
    x = Tomer() / Lior() / b'test'
    assert len(bytes(x)) == len(Tomer()) + len(Lior()) + len(b'test')
    assert x[Tomer].body_len == len(x)


def test_associativity():
    assert (Tomer() / Lior() / b'test') == (Tomer() / (Lior() / b'test')) == ((Tomer() / Lior()) / b'test')
