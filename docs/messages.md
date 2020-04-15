### Message
A message is a list-like composite of structs:
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

#### MetaField
Messages allow the usage of another type of field, called `MetaField`,

##### Length
Let's assume you want to include the length of the struct in the header.

The value of the `InclusiveLengthField` will be equal to the length of the
following structs of the message (including its own struct):
```python
from hydration import *

class Header1(Struct):
    message_len = InclusiveLengthField(UInt16)

class Body1(Struct):
    some_data = UInt64(0xAABB)
```
```pycon
print(Header1() / Body1())
Header1:
	message_len:	UInt16(10)
Body1:
	some_data:	UInt64(43707)
```
As you can see, the value of message_len is 10. (2 byte-long header, and 8 byte-long)

You can also use an `ExclusiveLengthField`. In which case, the field's length calculation 
<i>excludes</i> the length of its own struct:
```python
from hydration import *
class Header2(Struct):
    message_len = ExclusiveLengthField(UInt16)
```
```pycon
>>> print(Header2() / Body1())
Header2:
	message_len:	UInt16(8)
Body1:
	some_data:	UInt64(43707)
```
Now the value of message_len is 8.

##### Opcode
An `OpcodeField` will update automatically based on a given mapping
```python
from hydration import *
class Body2(Struct):
    data2 = UInt32(20)
class Body3(Struct):
    data3 = UInt64(40)

opcode_dict = {
    Body2: 1,
    Body3: 2,
}

class Header3(Struct):
    opcode = OpcodeField(UInt32, opcode_dict)
```
```pycon
>>> print(Header3() / Body2())
Header3:
	opcode:	UInt32(1)
Body2:
	data2:	UInt32(20)
>>> print(Header3() / Body3())
Header3:
	opcode:	UInt32(2)
Body3:
	data3:	UInt64(40)
```