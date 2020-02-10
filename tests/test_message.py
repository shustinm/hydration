import hydration as h


class Tomer(h.Struct):
    b = h.UInt8(5)
    c = h.Double(3)
    body_len = h.UInt16()


class Lior(h.Struct):
    a = h.Array(5)


def test_message():
    x = Tomer() / Lior() / Tomer()
    assert x[0] == x[Tomer] == x[(Tomer, 0)]
    assert x[-1] == x[(Tomer, 1)]
    assert len(x) == len(bytes(x))
    assert x[Tomer].body_len == len(Lior()) == len(x[Lior])
    assert bytes(x)


def test_bytes_suffix():
    x = Tomer() / Lior() / b'test'
    assert len(bytes(x)) == len(Tomer()) + len(Lior()) + len(b'test')
    print(x)


def test_associativity():
    assert (Tomer() / Lior() / b'test') == (Tomer() / (Lior() / b'test')) == ((Tomer() / Lior()) / b'test')