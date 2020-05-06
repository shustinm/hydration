import hydration as h


class IDVector(h.Struct):
    vec_len = h.UInt16()
    id_len = h.UInt8()
    vec = h.Vector(vec_len, h.FieldPlaceholder)  # Vector of IDs

    def __init__(self, id_type, *args, **kwargs):
        self.vec.type = id_type()
        self.id_len = len(self.vec.type)
        super().__init__(id_type, *args, **kwargs)


def test_id_vector():
    x = IDVector(h.UInt16).from_bytes(b'\x02\x00\x02\x00\x01\x01\x00')
    assert x.vec.value == (256, 1)
    assert x.id_len == 2
    assert IDVector(h.UInt16, vec=[256, 1]).vec_len == 2
    assert IDVector(h.UInt16, vec=[256, 1]).id_len == 2
    assert IDVector(h.UInt8, vec=[0, 1, 1, 0]).vec_len == 4
    assert IDVector(h.UInt8, vec=[0, 1, 1, 0]).id_len == 1
