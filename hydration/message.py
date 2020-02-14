import inspect
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import List

from .base import Struct
from .fields import Field
from .validators import Validator


class Message:
    def __init__(self, *layers, update_metadata: bool = True):

        self.layers: List[Struct] = []
        for layer in layers:
            # Messages are flat, they will not contain other messages, so just add its' layers
            if isinstance(layer, Message):
                self.layers.extend(layer.layers)
                continue
            # Check if we're appending bytes
            elif isinstance(layer, bytes):
                # If the last layer is already bytes, change it instead
                if isinstance(self.layers[-1], bytes):
                    self.layers[-1] += layer
                    continue
            elif not isinstance(layer, Struct):
                raise TypeError('Invalid type given: {}, expected: Message, Struct, or bytes'.format(type(layer), ))

            self.layers.append(layer)

        if update_metadata:
            self._update_metas()

    def serialize(self):
        return b''.join(bytes(layer) for layer in self.layers)

    def _update_metas(self):
        """
        Iterate over the layers in reversed order, and update all their MetaFields
        """
        for layer in reversed(self.layers):
            if isinstance(layer, bytes):
                continue

            for _, field in layer:
                if isinstance(field, MetaField):
                    field.update(self, layer)

    def __eq__(self, other):
        if isinstance(other, Message):
            return all(l1 == l2 for l1, l2 in zip(self, other))
        return False

    def __bytes__(self):
        return self.serialize()

    def __str__(self):
        # __str__ every layer and insert a line between each layer
        return '\n{}\n'.format('-' * 10).join(str(layer) for layer in self.layers)

    def __add__(self, other):
        return Message(self, other)

    def __truediv__(self, other):
        return Message(self, other)

    def __iter__(self):
        return iter(self.layers)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.layers[item]

        if inspect.isclass(item):
            occurrence_to_find = 0
        elif isinstance(item, tuple):
            item, occurrence_to_find = item
        else:
            raise TypeError

        occurrences = 0
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
        return sum(map(len, self.layers))


class MetaField(Field, ABC):
    """
    A Field that contains metadata (data about the message)
    """

    def __init__(self, data_field: Field):
        self.data_field = data_field

    @property
    def validator(self) -> Validator:
        return self.data_field.validator

    @validator.setter
    def validator(self, value):
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

    def __bytes__(self) -> bytes:
        return bytes(self.data_field)

    def from_bytes(self, data: bytes):
        return self.data_field.from_bytes(data)

    @abstractmethod
    def update(self, message: Message, struct: Struct):
        raise NotImplementedError


class InclusiveLengthField(MetaField):
    def update(self, message: Message, struct: Struct):
        self.value = len(message)
