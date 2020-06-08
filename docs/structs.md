### Struct
A struct is a composite of fields. 
To create a struct, Inherit from `Struct` to combine multiple fields:
```python
from hydration import *

class MyStruct(Struct):
    a = UInt8
    b = UInt8(value=3)  # You can set the default value
```

```pycon
>>> st = MyStruct(a=10)  # Structs can receive field values as keyword arguments
>>> print(st) 
MyStruct
    a:	UInt8(10)
    b:	UInt8(3)
>>> bytes(st)
b'\n\x03'
>>> print(MyStruct.from_bytes(b'\n\x03'))
MyStruct:
	a:	UInt8(10)
	b:	UInt8(3)
```
Structs are also mutable, so you can set field values without explicitly accessing their `value` property:
```pycon
>>> st = MyStruct(a=10)
>>> st.b = 5
>>> print(st)
MyStruct
    a:	UInt8(10)
    b:	UInt8(5)
```
#### Endianness
When defining a Struct, you may set the default Endianness for all of its scalars:
```python
from hydration import *

class Clean(Struct, endianness=BigEndian):
    a = UInt64
    b = UInt32
    c = UInt16(endianness=LittleEndian)
    d = UInt8
``` 
The endianness of the fields will always override the one of their struct. In this case, `c` will be in LittleEndian.

Note that endianness doesn't affect `d`, because it's a `UInt8`. It can't "have" endianness

#### Vectors
A vector is a dynamic length sequence. The length of the vector needs to be the value of another field in the struct.
```python
from hydration import *

class Dynamic(Struct):
    vec_len = UInt16()
    vector = Vector(length=vec_len)
``` 
```pycon
>>> st = Dynamic()
>>> st.vector = [1, 2, 3]
>>> print(st)
Dynamic:
	vec_len:	UInt16(3)
	vector:	Vector[1, 2, 3]
```
Notice that `vec_len` has been updated automatically.

By default, the vector is a sequence of `UInt8`, but this can be changed:
```python
from hydration import *

class Dynamic(Struct):
    vec_len = UInt16()
    vector = Vector(length=vec_len, field_type=UInt32)
``` 
```pycon
>>> st = Dynamic()
>>> st.vector = [1, 2, 3]
>>> bytes(st)
b'\x03\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00'
```

#### Inheritance
Sometimes, some structs have common fields, in which case - they can be separated to reduce code duplication:
```python
from hydration import *

class Common(Struct):
    common_a = UInt64

class Specific(Common):
    specific = UInt32
```
```pycon
>>> print(Specific())
Specific:
	common_a:	UInt64(0)
	specific:	UInt32(0)
```
Inheriting classes will prepend their fields before the fields of the subclass, to append them instead, use `footer=True`:
```python
from hydration import *

class CommonFooter(Struct, footer=True):
    common_a = UInt64

class Specific(CommonFooter):
    specific = UInt32
```
```pycon
>>> print(Specific())
Specific:
	specific:	UInt32(0)
	common_a:	UInt64(0)
```
Multiple inheritance is also possible, albeit not recommended:
```python
from hydration import *

class Header1(Struct):
    a = UInt8

class Header2(Struct):
    b = UInt8

class Specific(Header1, Header2):
    c = UInt16
```
```pycon
>>> print(Specific())
Specific:
	a:	UInt8(0)
	b:	UInt8(0)
	c:	UInt16(0)
```

Subclassing a `Struct` will only inherit the fields. It doesn't inherit `endianness` or `footer`. 