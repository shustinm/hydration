### Fields
Fields are the primitive objects that hold data, 
and can be converted to (and from) bytes
```pycon
>>> from hydration import *
>>> f = UInt16(1512)
>>> bytes(f)
b'\xe8\x05'
>>> UInt16().from_bytes(b'\xe8\x05')
UInt16(1512)
```

#### Scalars
Scalars are simple fields that represent low-level primitive data types:

| Scalar class | Size     |
| ------------ | -------- |
| `UInt8`      | 1 byte   |
| `UInt16`     | 2 bytes  |
| `UInt32`     | 4 bytes  |
| `UInt64`     | 8 bytes  |
| `Int8`       | 1 byte   |
| `Int16`      | 2 bytes  |
| `Int32`      | 4 bytes  |
| `Int64`      | 8 bytes  |
| `Float`      | 4 bytes  |
| `Double`     | 8 bytes  |

##### Validation
Fields have a `validator` keyword argument, you
```python
from hydration import *

range_ok = UInt8(validator=range(3))
list_ok = UInt8(validator=[10, 20])
```

```pycon
>>> range_ok.value = 4
ValueError: Given value 4 is not in range(0, 3)
>>> list_ok.value = 5
ValueError: Given value 5 is not in {0, 10, 20}
```

##### Endianness
You can control the endianness of scalars that are longer than 1 byte:
```pycon
>>> bytes(UInt32(3, endianness=BigEndian))
b'\x00\x00\x00\x03'
>>> bytes(UInt32(3, endianness=LittleEndian))
b'\x03\x00\x00\x00'
```
NOTE: The default endianness is that of your architecture, so it might be different on other processor architectures.

#### Sequences
Sequences are homogeneous collection of fields or structs, e.g. `Array` and `Vector`

##### Array
An array is a sequence of constant size
```pycon
>>> bytes(Array(3, value=[1, 2, 3]))
b'\x01\x02\x03'
```
By default, an `Array` is a construct of `UInt8`s, this can be changed.
```pycon
>>> bytes(Array(3, field_type=UInt16, value=[1, 2, 3]))
b'\x01\x00\x02\x00\x03\x00'
```
Notice that an `Array` has a fixed size. If the given value doesn't fill the array,
the rest of the scalars will have the default `field_type` value (usually 0):
```pycon
>>> print(Array(6, value=(3, 4)))
Array(3, 4, 0, 0, 0, 0)
>>> print(Array(5, field_type=UInt8(5), value=(3, 4)))
Array(3, 4, 5, 5, 5, 5)
```
##### Vector
Vectors are sequences of variable size, and can only be used inside a `Struct`. 