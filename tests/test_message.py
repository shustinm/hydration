import hydration as h


class Tomer(h.Header, h.Struct):
    _call_name = 'header'
    b = h.UInt8(5)
    c = h.Double(3)
    body_len = h.UInt16()


class Lior(h.Body, h.Struct):
    a = h.Array(5)

    @property
    def name(self):
        return 'body'



def test_message():
    x = Tomer() / Lior()
    print(x)