import hydration as h


class Tomer(h.Struct):
    b = h.UInt8(5)
    c = h.Double(3)


class Lior(h.Struct):
    a = h.Array(5)


def test_message():
    x = Tomer() / Lior() / Tomer()
    assert x[0] == x[Tomer] == x[(Tomer, 0)]
    assert x[-1] == x[(Tomer, 1)]
    assert x.size == len(bytes(x))


def test_bytes_suffix():
    x = Tomer() / Lior() / b'test'
    assert bytes(x) == b''.join((bytes(Tomer()), bytes(Lior()), b'test'))


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
        v = h.Vector('y')

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


def test_single():
    class T(h.Struct):
        x = h.InclusiveLengthField(h.UInt8)
        y = h.Array(10)

    t = h.Message(T())
    assert t[T].x == 11
