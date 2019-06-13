import hydration as h


class Omri(h.Struct):
    a = h.UInt16(256, endianness=h.Endianness.LittleEndian)
    b = h.UInt8(5)


if __name__ == '__main__':
    omri = Omri()
    print(omri)
    print(Omri.from_bytes(bytes(omri)))
