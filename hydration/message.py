import inspect
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import List, Union, Type, Mapping, Callable

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

    def update(self, message: Message, struct: Struct, struct_index: int):
        with suppress(IndexError):
            if not self.validator:
                self.validator = as_validator(set(self.opcode_dictionary.values()))
            self.value = self.opcode_dictionary[type(message[struct_index + 1])]
