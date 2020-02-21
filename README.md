# Hydration

![Tests](https://github.com/shustinm/hydration/workflows/Tests/badge.svg?branch=master)

<p align="center">
This software has been designed for you, with much joy, by <a href="http://github.shust.in">Michael Shustin</a>
</p>

---
<p>&nbsp;</p>
Hydration allows you to define python objects that can be converted to (and from) binary data.
<p>&nbsp;</p>

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
>>> st = MyStruct()
>>> print(st) 
MyStruct
    a:	UInt8(10)
    b:	UInt8(0)
```
You can see that `a` is already set at 10, let's set `b`:
```pycon
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