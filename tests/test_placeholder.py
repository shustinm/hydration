from typing import Type

import hydration as h
from hydration.fields import Field


class IDVector(h.Struct):
    vec_len = h.UInt16()
    id_len = h.UInt8()
    vec = h.Vector(vec_len, h.FieldPlaceholder)  # Vector of IDs

    def __init__(self, id_type: Type[Field] = h.FieldPlaceholder, *args, **kwargs):
        self.vec.type = id_type()
        self.id_len = len(self.vec.type)
        super().__init__(*args, **kwargs)

    @h.from_bytes_hook(vec)
    def set_vec_field(self):
        d = {len(x()): x for x in (h.UInt8, h.UInt16, h.UInt32, h.UInt32)}
        self.vec.type = d[int(self.id_len)]()


def test_id_vector():

    idv = IDVector(h.UInt8, vec=[0, 1, 1, 0])
    assert idv.vec_len == 4
    assert idv.id_len == 1
    assert IDVector.from_bytes(bytes(idv)) == idv

    idv = IDVector(h.UInt16, vec=[256, 1])
    assert idv.vec_len == 2
    assert idv.id_len == 2
    assert IDVector.from_bytes(bytes(idv)) == idv
