# Hydration

![Tests](https://github.com/shustinm/hydration/workflows/Tests/badge.svg?branch=master)

<p align="center">
This software has been designed for you, with much joy, by <a href="http://github.shust.in">Michael Shustin</a>
</p>

---
## Introduction
<p>&nbsp;</p>
Hydration allows you to define python objects that can be converted to (and from) binary data.
<p>&nbsp;</p>

<i>This guide assumes you are familiar with low-level primitive data types (like signed/unsigned int, int32, etc.) </i>

Let's start!
```python
from hydration import *
```


The most basic object in hydration is a `Field`. Most fields are pretty simple:
```pycon
>>> bytes(Int16(-1512))
b'\x18\xfa'
>>> bytes(UInt32(1512))
b'\xe8\x05\x00\x00'
```

You can also change the endianness of some fields:
```pycon
>>> bytes(UInt16(1512, endianness=Endianness.BigEndian))
b'\x05\xe8'
```

Inherit from `Struct` to combine multiple fields:
```python
from hydration import *

class MyStruct(Struct):
    
    # Default values usually come in handy in structs
    a = UInt8(10)  

    # Define a validator so only numbers up to 4 are valid
    b = UInt8(validator=RangeValidator(range(4)))
```

```pycon
>>> st = MyStruct(b=3)  # Structs can receive field values as keyword arguments
>>> print(st) 
MyStruct
    a:	UInt8(10)
    b:	UInt8(3)
>>> bytes(st)
b'\n\x03'
```
Structs are also mutable, so you can set field values after their creation.
```pycon
>>> st = MyStruct()
>>> st.b = 3
>>> print(st)
MyStruct
    a:	UInt8(10)
    b:	UInt8(3)
>>> bytes(st)
b'\n\x03'
```
Remember that we defined a validator? let's test it:
```pycon
>>> st.b = 4
ValueError: Given value 4 is not in range(0, 4)
```
### Fields
There are different kinds of fields, but they all have 2 things in common:
* Fields can be converted to (and from) bytes - by definition
* Fields can receive a `Validator`, to easily control which values are valid.

#### Scalars
Scalars are the most basic (and generic) fields, they are:
`UInt8`, `UInt16`, `UInt32`, `UInt64`, `Int8`, `Int16`, `Int32`, `Int64`, `Float`, `Double`.

You can control the endianness of scalars that take more than 1 byte:
```pycon
>>> bytes(UInt32(3, endianness=Endianness.BigEndian))
b'\x00\x00\x00\x03'
>>> bytes(UInt32(3, endianness=Endianness.LittleEndian))
b'\x03\x00\x00\x00'
```
NOTE: The default endianness is that of your architecture, so it might be different on other computers.

#### Sequence
Sequences are constructs of other fields or structs. The basic ones are: `Array` and `Vector`

##### Array
An array is a sequence of constant size, known during its' creation.
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
Vectors are sequences that are Vectors have to be used inside a Struct, 