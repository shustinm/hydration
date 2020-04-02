# Hydration

![Tests](https://github.com/shustinm/hydration/workflows/Tests/badge.svg?branch=master)

<p align="center">
This software has been designed for you, with much joy, by <a href="http://github.shust.in">Michael Shustin</a>
</p>

---

# What is Hydration?
Hydration is a library used to define python objects that can be converted to (and from) bytes.

## Introduction

<i>This guide assumes you are familiar with low-level primitive data types (like signed/unsigned int, int32, etc.) </i>

### Field
Fields are the primitive objects that hold data, 
and can be converted to (and from) bytes
```pycon
>>> from hydration import *
>>> f = UInt16(1512)
>>> bytes(f)
b'\xe8\x05'
```

### Struct
A struct is a composite of fields. 
To create a struct, Inherit from `Struct` to combine multiple `Field`s:
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
```

### Message
A message is a list-like composite of structs.
```python
from hydration import *

class Header(Struct):
    magic = UInt32(0xDEADBEEF)

class Body(Struct):
    param1 = Float(2.875)
    param2 = Int8(-128)
```
```pycon
>>> msg = Header() / Body()  # Create a message by using the division operator on structs
>>> print(msg)
Header:
	magic:	UInt32(3735928559)
Body:
	param1:	Float(2.875)
	param2:	Int8(-128)
>>> bytes(msg)
b'\xef\xbe\xad\xde\x00\x008@\x80'
```

### Advanced features
For more advanced usage, be sure to check the `docs/` folder.