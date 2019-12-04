import hydration as h


class Tomer(h.Struct):
    call_name = 'header'
    b = h.UInt8(5)
    c = h.Double(3)
    body_len = h.UInt16()
    body_opcode = None


class Lior(h.Struct):
    a = h.Array(5)
    call_name = 'body'


def test_message():
    x = Tomer() / Lior()
    assert x[0] == x['header']
    assert x[0] == x[Tomer]
    assert x[1] == x['body']
    assert len(x) == len(bytes(x))
    assert x[Tomer].body_len == len(Lior()) == len(x[Lior])
    assert bytes(x)