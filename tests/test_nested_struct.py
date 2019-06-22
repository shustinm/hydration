import hydration as h


class Time(h.Struct):
    time = h.UInt64(3)


class Log(h.Struct):
    data = h.UInt8(2)
    time = Time()


class Ron(h.Struct):
    a = h.UInt64(55)
    log = Log()
    b = h.UInt64(56)


def test_nested():
    a = Ron()
    assert a.from_bytes(bytes(a)) == a
