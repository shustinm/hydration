import inspect
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import List, Union, Type, Mapping, Callable
from bidict import bidict, ValueDuplicationError

from hydration.helpers import as_obj
from .base import Struct
from .fields import Field
from .validators import ValidatorABC, as_validator

FieldType = Union[Field, Struct, Type[Field], Type[Struct]]


class Message:
    def __init__(self, *layers, update_metadata: bool = True):

        self.layers: List[Struct] = []

        for layer in layers:
            # Messages are flat, they will not contain other messages, so just add its' layers
            if isinstance(layer, Message):
                self.layers.extend(layer.layers)
                continue
            elif isinstance(layer, (bytes, Struct)):
                self.layers.append(layer)
            else:
                raise TypeError('Invalid type given: {}, expected: Message, Struct, or bytes'.format(type(layer), ))

        if update_metadata:
            self._update_metas()

    def serialize(self):
        return b''.join(bytes(layer) for layer in self.layers)

    def _update_metas(self):
        """
        Iterate over the layers, and update all their MetaFields
        """
        for index, layer in list(enumerate(self.layers)):
            if isinstance(layer, bytes):
                continue

            for _, field in layer:
                if isinstance(field, MetaField):
                    field.update(self, layer, index)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key != 'layers':
            self._update_metas()

    def __eq__(self, other):
        if isinstance(other, Message):
            return all(l1 == l2 for l1, l2 in zip(self, other))
        return False

    def __bytes__(self):
        return self.serialize()

    def __str__(self):
        # __str__ every layer and insert a newline between each layer
        return '\n'.join(str(layer) for layer in self.layers)

    def __add__(self, other):
        return Message(self, other)

    def __truediv__(self, other):
        return Message(self, other)

    def __iter__(self):
        return iter(self.layers)

    def index(self, item):
        # Standard index types
        if isinstance(item, (int, slice)):
            return item
        # Simple class lookup
        if inspect.isclass(item):
            occurrence_to_find = 0
        # Indexed class lookup, item: Tuple[Type, int]
        # Find the item[1]-th occurrence of an instance of item[0]
        elif isinstance(item, tuple):
            item, occurrence_to_find = item
        elif isinstance(item, Struct):
            for index, layer in enumerate(self.layers):
                if item is layer:
                    return index
            else:
                raise KeyError(f"Couldn't find any layer that is {item}")
        else:
            raise TypeError('Invalid type for operation')

        occurrences = 0
        # Loop through the layers to find the required occurrence of item
        for index, layer in enumerate(self.layers):
            if isinstance(layer, item):
                if occurrence_to_find == occurrences:
                    return index
                else:
                    occurrences += 1

        if occurrences == 0:
            raise KeyError(f"Couldn't find any layer that's an instance of {item}")
        else:
            raise KeyError(f"Found only {occurrences + 1} occurrences of {item}, "
                           f"but expected to find at least {occurrence_to_find + 1}")

    def __getitem__(self, item):
        # Single item lookup (class and/or index based)
        if isinstance(item, (int, tuple, Struct)) or inspect.isclass(item):
            return self.layers[self.index(item)]
        # Slice lookup, should still return a Message
        elif isinstance(item, slice):
            return Message(*self.layers[item], update_metadata=False)
        else:
            raise TypeError

    def __setitem__(self, key, value, update_metas=True):
        # Single value insertion (class and/or index based)
        if isinstance(key, (int, tuple, Struct)) or inspect.isclass(key):
            self.layers[self.index(key)] = value
        elif isinstance(key, slice):
            slice_length = (key.start - key.stop) / key.step
            if slice_length != len(value):
                raise ValueError(f'Length of assigned value ({len(value)}) '
                                 f'doesn\'t match the length of the slice ({slice_length})')
            self.layers[key] = value
        if update_metas:
            self._update_metas()

    def __contains__(self, item):
        if isinstance(item, Struct) or issubclass(item, Struct):
            with suppress(KeyError):
                return bool(self[item])
        return False

    def __len__(self):
        return len(self.layers)

    @classmethod
    def from_bytes(cls, header_class: Type[Struct], data: bytes, *additional_classes: List[Type[Struct]]):
        """
        Create a message from bytes data, using a header with an OpcodeField.
        
        :param header_class: A struct class which is the header of the message
        :param data: Data containing the message (in bytes)
        :param additional_classes: Additional classes to deserialize after the header and the body
        :return: A message created from `data`,based on `header_class` and `additional_classes`
        """

        # Find the opcode field in the header
        for opcode_name, opcode_field in as_obj(header_class):
            if isinstance(opcode_field, OpcodeField):
                break
        else:
            raise ValueError(f'Header {header_class.__name__} must have an opcode field in order to deserialize a message')

        # Create the header object
        header = header_class.from_bytes(data)
        data = data[len(header):]

        # Extract body class from header's opcode field
        header_opcode_value = getattr(header, opcode_name).value
        body_class: Type[Struct] = bidict(opcode_field.opcode_dictionary).inverse[header_opcode_value]

        # Create the body
        body = body_class.from_bytes(data)
        data = data[len(body):]
        additional_layers = []

        # Add the additional classes
        for additional_struct in additional_classes:
            try:
                # Try to deserialize the struct as an header, if it doesn't have an OpcodeField
                # it will raise a ValueError and we will treat it as a normal struct
                msg = Message.from_bytes(additional_struct, data)
                additional_layers.extend(msg.layers)
                data = data[msg.size:]
            except ValueError:
                obj = additional_struct.from_bytes(data)
                additional_layers.append(obj)
                data = data[len(obj):]

        return cls(header, body, *additional_layers, update_metadata=False)

    @classmethod
    def from_stream(cls, header_class: Type[Struct], read_func: Callable[[int], bytes], *additional_classes: List[Type[Struct]]):
        """
        Create a message from bytes data, using a header with an OpcodeField.
        
        :param header_class: A struct class which is the header of the message
        :param read_func: The stream's reader function
        The function needs to receive an int as a positional parameter and return a bytes object.
        :param additional_classes: Additional classes to deserialize after the header and the body
        :return: A message created from `read_func`,based on `header_class` and `additional_classes`
        """

        # Find the opcode field in the header
        for opcode_name, opcode_field in as_obj(header_class):
            if isinstance(opcode_field, OpcodeField):
                break
        else:
            raise ValueError(f'Header {header_class.__name__} must have an opcode field in order to deserialize a message')

        # Create the header object
        header = header_class.from_stream(read_func)

        # Extract body class from header's opcode field
        header_opcode_value = getattr(header, opcode_name).value
        body_class: Type[Struct] = bidict(opcode_field.opcode_dictionary).inverse[header_opcode_value]

        # Create the body
        body = body_class.from_stream(read_func)
        additional_layers = []

        # Add the additional classes
        for additional_struct in additional_classes:
            try:
                # Try to deserialize the struct as an header, if it doesn't have an OpcodeField
                # it will raise a ValueError and we will treat it as a normal struct
                msg = Message.from_stream(additional_struct, read_func)
                additional_layers.extend(msg.layers)
            except ValueError:
                obj = additional_struct.from_stream(read_func)
                additional_layers.append(obj)

        return cls(header, body, *additional_layers, update_metadata=False)

    @property
    def size(self):
        # layers are structs or bytes, so use len instead of size
        return sum(len(layer) for layer in self.layers)


class MetaField(Field, ABC):
    """
    A Field that contains metadata (data about the message)
    """

    def __init__(self, data_field: FieldType):
        self.data_field = as_obj(data_field)

    @property
    def validator(self) -> ValidatorABC:
        return self.data_field.validator

    @validator.setter
    def validator(self, value: ValidatorABC):
        self.data_field.validator = value

    @property
    def value(self):
        return self.data_field.value

    @value.setter
    def value(self, value):
        self.data_field.value = value

    def __repr__(self) -> str:
        return repr(self.data_field)

    def __str__(self) -> str:
        return str(self.data_field)

    def __len__(self) -> int:
        return len(self.data_field)

    @property
    def size(self):
        return self.data_field.size

    def __bytes__(self) -> bytes:
        return bytes(self.data_field)

    def from_bytes(self, data: bytes):
        return self.data_field.from_bytes(data)

    def from_stream(self, read_func: Callable[[int], bytes]):
        return self.data_field.from_stream(read_func)

    @abstractmethod
    def update(self, message: Message, struct: Struct, struct_index: int):
        raise NotImplementedError


class InclusiveLengthField(MetaField):
    def update(self, message: Message, struct: Struct, struct_index: int):
        self.value = message[struct_index:].size


class ExclusiveLengthField(MetaField):
    def update(self, message: Message, struct: Struct, struct_index: int):
        # Slicing doesn't raise IndexError #yolo
        self.value = message[struct_index + 1:].size


class OpcodeField(MetaField):
    def __init__(self, data_field: FieldType, opcode_dictionary: Mapping):
        super().__init__(data_field)
        self.opcode_dictionary = opcode_dictionary
        
        try:
            # Validate that there are no duplicate opcodes
            bidict(opcode_dictionary)
        except ValueDuplicationError:
            raise ValueError("Opcode values must be unique")

    def update(self, message: Message, struct: Struct, struct_index: int):
        with suppress(IndexError):
            if not self.validator:
                self.validator = as_validator(set(self.opcode_dictionary.values()))
            self.value = self.opcode_dictionary[type(message[struct_index + 1])]
