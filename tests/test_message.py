import pytest
import hydration as h


class Tomer(h.Struct):
    b = h.UInt8(5)
    c = h.Double(3)
    data_len = h.UInt16()
    _meta_down = {'len': data_len}

    @property
    def name(self):
        return 'header'

    @property
    def meta_down(self):
        return self._metadown


class Lior(h.Struct):
    a = h.Array(5)

    @property
    def name(self):
        return 'body'

    @property
    def meta_up(self):
        return {
            'len': len(self)
        }


def test_message():
    x = Tomer() / Lior()
    print(x)