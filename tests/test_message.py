import hydration as h


class Tomer(h.Struct):
    b = h.UInt8(5)
    c = h.Double(3)
    data_len = h.UInt16()

    h.Struct.add_body_connection('len', data_len)

    @property
    def name(self):
        return 'header'


class Lior(h.Struct):
    a = h.Array(5)

    h.Struct.add_header_connection('len', len)

    @property
    def name(self):
        return 'body'



def test_message():
    x = Tomer() / Lior()
    print(x)