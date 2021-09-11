import hydration as h


def test_scalar():

    class Maor(h.Struct):
        a: h.UInt8 = 3

    assert bytes(Maor()) == b'\x03'


def test_sequence():

    class Raz(h.Struct):
        b: h.UInt8[10] = {0}

    class G(h.Struct):
        c: h.UInt8[10] = {9}

    assert bytes(Raz()) == b'\x00' * 10
    assert bytes(G()) == b'\x09' * 10

    class Koren(h.Struct):
        bad: h.UInt8[10] = {300}

    Koren()

    bytes(Koren())
