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
Fields have a `validator` keyword argument, which allows you catch errors during early
stages of the object creation, whether by construction or `from_bytes`
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


##### Enum
Enums are scalars that makes working with `enum.IntEnum` easier.
```python
from enum import IntEnum

class Color(IntEnum):
    RED = 1
    GREEN = 2
    BLUE = 3
```
By using enums, you get clean, readable code. The constructor receives the class of the Enum
and takes care of initialization and validation for you. (The default value is the first enum)
```pycon
>>> field = Enum(UInt8, Color)
>>> field.name
'RED'
>>> field.value
1
>>> field.value = 4
ValueError: 4 is not a valid Color
```

#### Sequences
Sequences are homogeneous collection of fields or structs, e.g. `Array` and `Vector`

##### Array
Arrays are sequences of constant size
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
Vectors are sequences of variable size, and can only be used inside a `Struct`,
so it is documented in [docs/struct.md](https://github.com/shustinm/hydration/blob/master/docs/structs.md#vectors)