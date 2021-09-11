from zlib import crc32

import pytest

import hydration as h


class Tomer(h.Struct):
    b = h.UInt8(5)
    c = h.Double(3)


class Lior(h.Struct):
    a: h.UInt8[5] = {0}


def test_message():
    first = Tomer()
    last = Tomer()
    x = first / Lior() / last
    assert x[0] == x[Tomer] == x[(Tomer, 0)]
    assert x[-1] == x[(Tomer, 1)]
    assert x.size == len(bytes(x))
    assert x[-1] is last
    assert Tomer in x
    assert Lior in x

    class LiTor(h.Struct):
        pass

    assert LiTor not in x

    assert first in x
    assert last in x
    assert Tomer() not in x
    assert LiTor() not in x

    with pytest.raises(TypeError):
        assert 3 not in x

    x[last] = Tomer(b=124)
    assert x[-1].b == 124


def test_bytes_suffix():
    x = Tomer() / Lior() / b'test'
    assert bytes(x) == b''.join((bytes(Tomer()), bytes(Lior()), b'test'))


def test_suffix_with_length():
    class Header(h.Struct):
        length = h.InclusiveLengthField(h.UInt16)

    Header() / b'lomeshane'


def test_associativity():
    assert (Tomer() / Lior() / b'test') == (Tomer() / (Lior() / b'test')) == ((Tomer() / Lior()) / b'test')


def test_length_fields():
    class A(h.Struct):
        a = h.UInt16
        length_field = h.ExclusiveLengthField(h.UInt16)

    class B(h.Struct):
        a = h.UInt16
        length_field = h.InclusiveLengthField(h.UInt16)

    class C(h.Struct):
        x = h.Array(5)
        y = h.UInt8

    class D(h.Struct):
        v = h.Vector(length='y')

    msg = A() / B()

    assert msg[A].length_field == msg[B].length_field == len(B())

    msg /= C()

    assert msg[A].length_field == msg[B].length_field == len(B()) + len(C())

    the_d = D(v=[1, 2, 3])
    msg /= the_d

    assert msg[A].length_field == msg[B].length_field == len(B()) + len(C()) + len(the_d)


def test_opcode_field():

    class C1(h.Struct):
        x = h.UInt32

    b_opcodes = {
        C1: 3
    }

    class B1(h.Struct):
        data = h.UInt8

    class B2(h.Struct):
        opcode = h.OpcodeField(h.UInt8, b_opcodes)

    a_opcodes = {
        B1: 1,
        B2: 2
    }

    class A(h.Struct):
        opcode = h.OpcodeField(h.UInt8, a_opcodes)

    assert (A() / B1())[A].opcode == 1
    assert (A() / B2())[A].opcode == 2

    assert (A() / B2() / C1())[B2].opcode == 3

    m = A() / B1()
    assert m[A].opcode == 1

    m[B1] = B2()
    assert m[A].opcode == 2


def test_single():
    class T(h.Struct):
        x = h.InclusiveLengthField(h.UInt8)
        y = h.Array(10, fill=True)

    t = h.Message(T())
    assert t[T].x == 11


class _CRCField(h.message.MetaField):
    def __init__(self):
        # Only UInt32 is supported
        super().__init__(h.UInt32)

    def update(self, message: h.Message, struct: h.Struct, struct_index: int):
        self.value = crc32(bytes(message[:struct_index + 1])[:-4])


class Header(h.Struct, endianness=h.BigEndian):
    magic = h.UInt32(0x01052000)
    body_length = h.ExclusiveLengthField(h.UInt16)


class Footer(h.Struct, endianness=h.BigEndian):
    crc = _CRCField()


def test_crc():
    msg = Header(magic=0x01052000) / Footer()
    assert crc32(bytes(msg)[:-4]) == msg[Footer].crc.value
