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
Structs are also mutable, so you can set field values after their creation.
```pycon
>>> st = MyStruct(a=10)
>>> st.b = 5
>>> print(st)
MyStruct
    a:	UInt8(10)
    b:	UInt8(5)
```

#### [WIP] Inheritance
#### [WIP] Vectors
