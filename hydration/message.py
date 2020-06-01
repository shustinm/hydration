import inspect
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import List, Union, Type, Mapping

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
        Iterate over the layers in reversed order, and update all their MetaFields
        """
        for index, layer in reversed(list(enumerate(self.layers))):
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

    def __getitem__(self, item):
        # Index lookup
        if isinstance(item, int):
            return self.layers[item]
        # Slice lookup, should still return a Message
        elif isinstance(item, slice):
            m = Message()
            # Copy the layers without calling __init__, avoids invoking update_metas
            m.layers = self.layers[item]
            return m

        # Simple class lookup
        if inspect.isclass(item):
            occurrence_to_find = 0
        # Indexed class lookup, item: Tuple[Type, int]
        # Find the item[1]-th occurrence of an instance of item[0]
        elif isinstance(item, tuple):
            item, occurrence_to_find = item
        else:
            raise TypeError

        occurrences = 0
        # Loop through the layers to find the required occurrence of item
        for layer in self.layers:
            if isinstance(layer, item):
                if occurrence_to_find == occurrences:
                    return layer
                else:
                    occurrences += 1

        if occurrences == 0:
            raise KeyError(f"Couldn't find any layer that's an instance of {item}")
        else:
            raise KeyError(f"Found only {occurrences + 1} occurrences of {item}, "
                           f"but expected to find at least {occurrence_to_find + 1}")

    def __contains__(self, item):
        with suppress(KeyError):
            return bool(self[item])

        return item in self.layers

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

    def from_bytes(self, data: bytes):
        return self.data_field.from_bytes(data)

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
